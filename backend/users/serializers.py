from rest_framework import serializers

from .models import Entity, KYCStatus, User, UserRole


class UserPublicSerializer(serializers.ModelSerializer):
    country = serializers.CharField(source="country_code")
    isVerified = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "email", "handle", "country", "isVerified", "role")
        read_only_fields = fields

    def get_isVerified(self, obj: User) -> bool:
        return obj.kyc_status == KYCStatus.APPROVED

    def get_role(self, obj: User) -> str:
        return obj.role


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    handle = serializers.CharField(max_length=30)
    country = serializers.CharField(max_length=2)
    role = serializers.ChoiceField(choices=["talent", "employer"])

    def validate_handle(self, value: str) -> str:
        if User.objects.filter(handle__iexact=value).exists():
            raise serializers.ValidationError("Handle already taken.")
        return value.lower()

    def create(self, validated_data):
        role_map = {"talent": UserRole.TALENT, "employer": UserRole.EMPLOYER}
        handle = validated_data["handle"]
        user = User(
            username=handle,
            email=validated_data["email"].lower(),
            handle=handle,
            role=role_map[validated_data["role"]],
            country_code=validated_data["country"].upper(),
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "handle",
            "role",
            "country_code",
            "tier",
            "kyc_status",
            "verified_badge",
            "date_joined",
        )
        read_only_fields = ("id", "verified_badge", "date_joined")


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password",
            "handle",
            "role",
            "country_code",
        )

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class EntitySerializer(serializers.ModelSerializer):
    user_handle = serializers.CharField(source="user.handle", read_only=True)

    class Meta:
        model = Entity
        fields = (
            "id",
            "user",
            "user_handle",
            "kyb_status",
            "business_type",
            "registration_no",
        )
        read_only_fields = ("id", "user_handle")
