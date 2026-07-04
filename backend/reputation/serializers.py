from rest_framework import serializers

from .models import Reference


class ReferenceSerializer(serializers.ModelSerializer):
    user_handle = serializers.CharField(source="user.handle", read_only=True)
    listing_title = serializers.CharField(source="listing.title", read_only=True)
    employer_handle = serializers.SerializerMethodField()

    class Meta:
        model = Reference
        fields = (
            "id",
            "user",
            "user_handle",
            "listing",
            "listing_title",
            "employer_handle",
            "signed_proof",
            "signature_hash",
            "signature_b64",
            "issued_at",
        )
        read_only_fields = fields


class ProofOfWorkCredentialSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    job_title = serializers.CharField()
    field = serializers.CharField()
    tier = serializers.CharField()
    completed_at = serializers.CharField()
    signed_by = serializers.CharField()
    signature_hash = serializers.CharField()
    verify_url = serializers.CharField()
