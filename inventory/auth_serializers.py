from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Extends the JWT payload and login response with role + username.
    Frontend reads role from the response to build the right UI.
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Embed role in the token so the frontend doesn't need a /me call
        token['role']     = user.role
        token['username'] = user.username
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # Also include role/username in the response body
        data['role']     = self.user.role
        data['username'] = self.user.username
        data['user_id']  = self.user.id
        return data


class UserSerializer(serializers.ModelSerializer):
    """Read serializer for listing / retrieving users."""

    class Meta:
        model  = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'phone', 'is_active_employee', 'is_active',
            'date_joined', 'last_login',
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']


class UserCreateSerializer(serializers.ModelSerializer):
    """Write serializer for creating new users (Admin only)."""

    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model  = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                  'password', 'role', 'phone']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Write serializer for updating users (Admin only). Password optional."""

    password = serializers.CharField(write_only=True, min_length=8, required=False)

    class Meta:
        model  = User
        fields = ['username', 'email', 'first_name', 'last_name',
                  'password', 'role', 'phone', 'is_active_employee', 'is_active']

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class MeSerializer(serializers.ModelSerializer):
    """Lightweight serializer for /api/auth/me/ — current user info."""

    class Meta:
        model  = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                  'role', 'phone', 'is_active_employee']
        read_only_fields = fields
