from rest_framework import serializers
from rest_framework_gis.serializers import GeometryField

from core.embeddings import EMBEDDING_DIMENSIONS
from users.models import User, UserRole

from .models import Application, Listing, ListingMode


class ListingSerializer(serializers.ModelSerializer):
    geo_point = GeometryField(required=False, allow_null=True)
    owner_handle = serializers.CharField(source="owner.handle", read_only=True)
    distance_km = serializers.FloatField(read_only=True, required=False)

    class Meta:
        model = Listing
        fields = (
            "id",
            "owner",
            "owner_handle",
            "title",
            "description",
            "field",
            "tier",
            "mode",
            "country_code",
            "geo_point",
            "currency",
            "budget",
            "escrow_id",
            "status",
            "skill_tags",
            "distance_km",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "owner", "owner_handle", "skill_tags", "distance_km", "created_at", "updated_at")

    def validate(self, attrs):
        mode = attrs.get("mode", getattr(self.instance, "mode", None))
        geo_point = attrs.get(
            "geo_point",
            getattr(self.instance, "geo_point", None) if self.instance else None,
        )

        if mode == ListingMode.REMOTE and geo_point is not None:
            raise serializers.ValidationError(
                {"geo_point": "Remote listings must not include a geo_point."}
            )
        if mode in (ListingMode.ONSITE, ListingMode.HYBRID) and geo_point is None:
            raise serializers.ValidationError(
                {"geo_point": "On-site and hybrid listings require a geo_point."}
            )
        return attrs


class ListingFeedSerializer(serializers.ModelSerializer):
    """Flattened serializer aligned with the React job feed."""

    owner_handle = serializers.CharField(source="owner.handle", read_only=True)
    is_verified_employer = serializers.BooleanField(
        source="owner.verified_badge", read_only=True
    )
    distance_km = serializers.FloatField(read_only=True, required=False)

    class Meta:
        model = Listing
        fields = (
            "id",
            "title",
            "description",
            "field",
            "tier",
            "mode",
            "country_code",
            "currency",
            "budget",
            "owner_handle",
            "is_verified_employer",
            "skill_tags",
            "distance_km",
            "geo_point",
            "status",
            "created_at",
        )


class ApplicationSerializer(serializers.ModelSerializer):
    listing_title = serializers.CharField(source="listing.title", read_only=True)
    talent_handle = serializers.CharField(source="talent.handle", read_only=True)

    class Meta:
        model = Application
        fields = (
            "id",
            "listing",
            "listing_title",
            "talent",
            "talent_handle",
            "status",
            "cover_note",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "listing_title",
            "talent_handle",
            "created_at",
            "updated_at",
        )

    def validate_talent(self, talent: User):
        if talent.role != UserRole.TALENT:
            raise serializers.ValidationError("Only talent users may apply to listings.")
        return talent


class JobMatchRequestSerializer(serializers.Serializer):
    embedding = serializers.ListField(
        child=serializers.FloatField(),
        min_length=EMBEDDING_DIMENSIONS,
        max_length=EMBEDDING_DIMENSIONS,
    )
    lat = serializers.FloatField(required=False, allow_null=True)
    lng = serializers.FloatField(required=False, allow_null=True)
    limit = serializers.IntegerField(default=20, min_value=1, max_value=100)
    country_code = serializers.CharField(required=False, allow_blank=True, max_length=2)
    max_geo_km = serializers.FloatField(default=200.0, min_value=1, max_value=500)
    engine = serializers.ChoiceField(choices=["orm", "sql"], default="orm")

    def validate(self, attrs):
        lat, lng = attrs.get("lat"), attrs.get("lng")
        if (lat is None) ^ (lng is None):
            raise serializers.ValidationError("Provide both lat and lng for geo-weighting.")
        if lat is not None and not (-90 <= lat <= 90):
            raise serializers.ValidationError({"lat": "Must be between -90 and 90."})
        if lng is not None and not (-180 <= lng <= 180):
            raise serializers.ValidationError({"lng": "Must be between -180 and 180."})
        if len(attrs["embedding"]) != EMBEDDING_DIMENSIONS:
            raise serializers.ValidationError(
                {"embedding": f"Must contain exactly {EMBEDDING_DIMENSIONS} dimensions."}
            )
        return attrs

