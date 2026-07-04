from rest_framework import serializers

from .models import CountryVerificationBadge, VerificationSession


class VerificationSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerificationSession
        fields = (
            "id",
            "provider",
            "external_session_id",
            "status",
            "redirect_url",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class CountryVerificationBadgeSerializer(serializers.ModelSerializer):
    user_handle = serializers.CharField(source="user.handle", read_only=True)

    class Meta:
        model = CountryVerificationBadge
        fields = (
            "id",
            "user",
            "user_handle",
            "country_code",
            "label",
            "provider",
            "minted_at",
        )
        read_only_fields = fields
