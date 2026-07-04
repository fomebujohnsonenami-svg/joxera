from rest_framework import serializers

from .models import Escrow, EscrowState, Wallet, WalletTransaction


class WalletSerializer(serializers.ModelSerializer):
    user_handle = serializers.CharField(source="user.handle", read_only=True)

    class Meta:
        model = Wallet
        fields = (
            "id",
            "user",
            "user_handle",
            "currency",
            "balance",
            "rail",
            "updated_at",
        )
        read_only_fields = ("id", "user_handle", "balance", "updated_at")


class WalletTransactionSerializer(serializers.ModelSerializer):
    listing_title = serializers.SerializerMethodField()

    class Meta:
        model = WalletTransaction
        fields = (
            "id",
            "tx_type",
            "amount",
            "currency",
            "balance_after",
            "description",
            "listing_title",
            "metadata",
            "created_at",
        )

    def get_listing_title(self, obj: WalletTransaction) -> str | None:
        if obj.escrow_id and obj.escrow.listing_id:
            return obj.escrow.listing.title
        return None


class EscrowSerializer(serializers.ModelSerializer):
    listing_title = serializers.CharField(source="listing.title", read_only=True)
    employer_handle = serializers.CharField(source="employer.handle", read_only=True)
    talent_handle = serializers.CharField(source="talent.handle", read_only=True, allow_null=True)
    both_signed_off = serializers.BooleanField(read_only=True)

    class Meta:
        model = Escrow
        fields = (
            "id",
            "listing",
            "listing_title",
            "employer",
            "employer_handle",
            "talent",
            "talent_handle",
            "amount",
            "currency",
            "state",
            "provider",
            "provider_ref",
            "employer_signed_off",
            "talent_signed_off",
            "both_signed_off",
            "funded_at",
            "released_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "listing_title",
            "employer_handle",
            "talent_handle",
            "both_signed_off",
            "funded_at",
            "released_at",
            "created_at",
            "updated_at",
        )


class EscrowTimelineSerializer(serializers.Serializer):
    escrow_id = serializers.IntegerField()
    listing_title = serializers.CharField()
    amount = serializers.DecimalField(max_digits=14, decimal_places=2)
    currency = serializers.CharField()
    state = serializers.ChoiceField(choices=EscrowState.choices)
    employer_signed_off = serializers.BooleanField()
    talent_signed_off = serializers.BooleanField()
    funded_at = serializers.DateTimeField(allow_null=True)
    released_at = serializers.DateTimeField(allow_null=True)
    steps = serializers.ListField(child=serializers.DictField())


class ReleaseEscrowSerializer(serializers.Serializer):
    escrow_id = serializers.IntegerField()


class FundEscrowSerializer(serializers.Serializer):
    escrow_id = serializers.IntegerField()
    use_wallet = serializers.BooleanField(default=False)


class CreateEscrowSerializer(serializers.Serializer):
    listing_id = serializers.IntegerField()
    talent_id = serializers.IntegerField(required=False, allow_null=True)
