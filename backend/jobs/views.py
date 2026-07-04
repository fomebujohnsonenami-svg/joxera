from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from verification.permissions import IsVerifiedUser

from .filters import ListingFilterSet
from .models import Application, Listing, ListingMode, ListingStatus
from .serializers import (
    ApplicationSerializer,
    JobMatchRequestSerializer,
    ListingFeedSerializer,
    ListingSerializer,
)
from .services.matcher import match_listings_for_talent, match_listings_raw_sql
from .tasks import parse_and_embed_listing


class JobFeedPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 100


def _published_queryset(user=None):
    qs = Listing.objects.select_related("owner")
    if user and user.is_authenticated:
        return qs.filter(
            Q(status=ListingStatus.PUBLISHED) | Q(owner=user)
        )
    return qs.filter(status=ListingStatus.PUBLISHED)


class ListingViewSet(viewsets.ModelViewSet):
    """
    Job listings — public read for published posts;
    mutating requests require identity verification (KYC approved).
    """

    serializer_class = ListingSerializer
    filterset_class = ListingFilterSet
    pagination_class = JobFeedPagination

    def get_queryset(self):
        return _published_queryset(self.request.user)

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return [IsAuthenticated(), IsVerifiedUser()]

    def perform_create(self, serializer):
        listing = serializer.save(owner=self.request.user, status=ListingStatus.PUBLISHED)
        parse_and_embed_listing.delay(listing.id)


class ApplicationViewSet(viewsets.ModelViewSet):
    """Job applications — mutating requests require identity verification."""

    queryset = Application.objects.select_related("listing", "talent").all()
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated, IsVerifiedUser]

    def perform_create(self, serializer):
        serializer.save(talent=self.request.user)


class CountryJobFeedView(APIView):
    """
    Country-scoped feed for remote (and optionally hybrid) listings.

    GET /api/countries/{country_code}/jobs/?field=&mode=&tier=
    """

    permission_classes = [AllowAny]
    pagination_class = JobFeedPagination

    def get(self, request, country_code: str):
        qs = _published_queryset().filter(country_code=country_code.upper())

        # Default to remote/global unless caller specifies mode
        mode = request.query_params.get("mode")
        if not mode:
            qs = qs.filter(mode=ListingMode.REMOTE)
        elif mode == "all":
            pass
        else:
            qs = qs.filter(mode=mode)

        filterset = ListingFilterSet(request.query_params, queryset=qs, request=request)
        if not filterset.is_valid():
            return Response(filterset.errors, status=status.HTTP_400_BAD_REQUEST)

        paginator = JobFeedPagination()
        page = paginator.paginate_queryset(filterset.qs.order_by("-created_at"), request)
        serializer = ListingFeedSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class NearbyJobsView(APIView):
    """
    Geospatial proximity feed for on-site and hybrid listings.

    GET /api/v3/global/jobs/nearby/?lat=&lng=&radiusKm=&field=&mode=&tier=&country=
    """

    permission_classes = [AllowAny]
    pagination_class = JobFeedPagination

    def get(self, request):
        try:
            lat = float(request.query_params["lat"])
            lng = float(request.query_params["lng"])
            radius_km = float(request.query_params.get("radiusKm", 15))
        except (KeyError, TypeError, ValueError):
            return Response(
                {"detail": "Required query params: lat, lng. Optional: radiusKm (default 15)."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not (-90 <= lat <= 90 and -180 <= lng <= 180):
            return Response({"detail": "Invalid lat/lng."}, status=status.HTTP_400_BAD_REQUEST)

        if radius_km <= 0 or radius_km > 500:
            return Response(
                {"detail": "radiusKm must be between 0 and 500."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        origin = Point(lng, lat, srid=4326)

        qs = (
            _published_queryset()
            .filter(
                mode__in=[ListingMode.ONSITE, ListingMode.HYBRID],
                geo_point__isnull=False,
            )
            .annotate(distance=Distance("geo_point", origin))
            .filter(geo_point__distance_lte=(origin, D(km=radius_km)))
            .order_by("distance")
        )

        filterset = ListingFilterSet(request.query_params, queryset=qs, request=request)
        if not filterset.is_valid():
            return Response(filterset.errors, status=status.HTTP_400_BAD_REQUEST)

        paginator = JobFeedPagination()
        page = paginator.paginate_queryset(filterset.qs, request)

        results = []
        for listing in page:
            data = ListingFeedSerializer(listing).data
            if hasattr(listing, "distance") and listing.distance is not None:
                data["distance_km"] = round(listing.distance.km, 2)
            results.append(data)

        return paginator.get_paginated_response(results)


class JobMatchView(APIView):
    """
    Universal skill matching — cosine similarity against listing embeddings.

    POST /api/v3/global/jobs/match/
    Body: { "embedding": [...768 floats], "lat": 6.52, "lng": 3.38, "limit": 20 }

    On-site/hybrid listings are weighted by geo-distance when lat/lng are provided.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = JobMatchRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if data.get("engine") == "sql":
            results = match_listings_raw_sql(
                talent_embedding=data["embedding"],
                lat=data.get("lat"),
                lng=data.get("lng"),
                limit=data["limit"],
                country_code=data.get("country_code") or None,
            )
            return Response({"count": len(results), "results": results})

        matches = match_listings_for_talent(
            talent_embedding=data["embedding"],
            lat=data.get("lat"),
            lng=data.get("lng"),
            limit=data["limit"],
            country_code=data.get("country_code") or None,
            max_geo_km=data.get("max_geo_km", 200.0),
        )

        return Response(
            {
                "count": len(matches),
                "results": [m.to_dict() for m in matches],
            }
        )
