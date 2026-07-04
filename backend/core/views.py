from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import CountryConfig
from .serializers import CountryConfigSerializer


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    return Response(
        {
            "status": "ok",
            "service": "joxera-backend",
            "message": "Borderless employment marketplace API",
        }
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def global_config(request):
    """
    Return regional parameters for the caller's detected country.

    Country is resolved by GeoIPMiddleware and available on ``request.country``.
    Pass ``?country=XX`` to request a specific region (must be configured).
    """
    country_code = (
        request.query_params.get("country", "").strip().upper()
        or getattr(request, "country", "US")
    )

    config = CountryConfig.objects.filter(
        country_code=country_code, is_active=True
    ).first()

    if config is None:
        config = CountryConfig.objects.filter(is_active=True).order_by("country_code").first()

    if config is None:
        return Response(
            {"detail": "No country configuration available."},
            status=503,
        )

    detected_via = "query" if request.query_params.get("country") else getattr(
        request, "country_detected_via", "fallback"
    )

    available = CountryConfig.objects.filter(is_active=True).order_by("country_code")

    payload = {
        "country_code": config.country_code,
        "country_name": config.country_name,
        "currency": config.currency,
        "payout_rail": config.default_payment_rail,
        "detected_via": detected_via,
        "available_countries": CountryConfigSerializer(available, many=True).data,
    }

    return Response(payload)
