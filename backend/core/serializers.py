from rest_framework import serializers

from .models import CountryConfig


class CountryConfigSerializer(serializers.ModelSerializer):
    payout_rail = serializers.CharField(source="default_payment_rail")

    class Meta:
        model = CountryConfig
        fields = (
            "country_code",
            "country_name",
            "currency",
            "payout_rail",
            "default_payment_rail",
        )


class GlobalConfigSerializer(serializers.Serializer):
    country_code = serializers.CharField()
    country_name = serializers.CharField()
    currency = serializers.CharField()
    payout_rail = serializers.CharField()
    detected_via = serializers.CharField()
    available_countries = CountryConfigSerializer(many=True)
