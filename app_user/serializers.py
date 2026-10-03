from rest_framework import serializers
from rest_framework.authentication import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User


class SignUpSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    password = serializers.CharField(write_only=True)
    confirmation_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'phone_number', 'username', 'password', 'confirmation_password']

    def validate(self, attrs):
        if attrs.get("password") != attrs.get("confirmation_password"):
            raise serializers.ValidationError({
                "confirmation_password": "Parol va tasdiqlash paroli mos emas!"
            })
        return attrs

    def create(self, validated_data):
        validated_data.pop("confirmation_password")
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(username=attrs.get("username"), password=attrs.get("password"))
        if user is None:
            raise serializers.ValidationError({"detail": "Username yoki parol noto'g'ri!"})
        
        attrs["user"] = user
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone_number']
        read_only_fields = ['id', 'username']