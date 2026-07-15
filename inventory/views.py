from rest_framework import generics, filters, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Product, ProductForecast, User
from .serializers import ProductSerializer, ProductForecastSerializer
from .auth_serializers import (
    CustomTokenObtainPairSerializer,
    UserSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    MeSerializer,
)
from .permissions import IsAdmin, IsManagerOrAdmin, IsAnyRole, ReadOnlyOrManagerAbove


# ─────────────────────────────────────────────
# Auth views
# ─────────────────────────────────────────────

class CustomTokenObtainPairView(TokenObtainPairView):
    """POST /api/auth/login/ — returns access, refresh, role, username."""
    serializer_class = CustomTokenObtainPairSerializer


class MeView(APIView):
    """GET /api/auth/me/ — returns the current user's profile."""
    permission_classes = [IsAnyRole]

    def get(self, request):
        serializer = MeSerializer(request.user)
        return Response(serializer.data)


# ─────────────────────────────────────────────
# User management (Admin only)
# ─────────────────────────────────────────────

class UserViewSet(viewsets.ModelViewSet):
    """
    Admin-only CRUD on users.
    GET    /api/users/          — list all users
    POST   /api/users/          — create user
    GET    /api/users/<id>/     — retrieve user
    PATCH  /api/users/<id>/     — update user
    DELETE /api/users/<id>/     — deactivate user (soft delete)
    POST   /api/users/<id>/deactivate/ — toggle is_active_employee
    """
    queryset = User.objects.all().order_by('date_joined')
    permission_classes = [IsAdmin]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        if self.action in ('update', 'partial_update'):
            return UserUpdateSerializer
        return UserSerializer

    def destroy(self, request, *args, **kwargs):
        # Soft-delete: deactivate instead of hard delete
        user = self.get_object()
        user.is_active_employee = False
        user.is_active = False
        user.save()
        return Response({'detail': 'User deactivated.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        user = self.get_object()
        user.is_active_employee = not user.is_active_employee
        user.save()
        return Response({'is_active_employee': user.is_active_employee})


# ─────────────────────────────────────────────
# Product views
# ─────────────────────────────────────────────

class ProductListView(generics.ListCreateAPIView):
    """
    GET    /api/products/  — list products (all roles)
    POST   /api/products/  — create product (manager/admin only)
    """
    serializer_class   = ProductSerializer
    permission_classes = [ReadOnlyOrManagerAbove]
    filter_backends    = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields    = ['product_id', 'current_stock', 'name', 'category']
    search_fields      = ['product_id', 'name']
    ordering           = ['product_id']

    def get_queryset(self):
        queryset     = Product.objects.filter(is_active=True)
        category     = self.request.query_params.get('category')
        needs_reorder = self.request.query_params.get('needs_reorder')
        if category:
            queryset = queryset.filter(category=category)
        if needs_reorder and needs_reorder.lower() == 'true':
            from django.db.models import F
            queryset = queryset.filter(current_stock__lte=F('reorder_point'))
        return queryset


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/products/<product_id>/  — retrieve (all roles)
    PATCH  /api/products/<product_id>/  — update  (manager/admin)
    DELETE /api/products/<product_id>/  — delete  (admin only)
    """
    queryset           = Product.objects.all()
    serializer_class   = ProductSerializer
    permission_classes = [ReadOnlyOrManagerAbove]
    lookup_field       = 'product_id'

    def destroy(self, request, *args, **kwargs):
        if request.user.role != 'admin':
            return Response(
                {'detail': 'Only admins can delete products.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)


# ─────────────────────────────────────────────
# Forecast views
# ─────────────────────────────────────────────

class ProductForecastListView(generics.ListAPIView):
    """
    GET /api/forecasts/  — all roles can view forecasts.
    """
    serializer_class   = ProductForecastSerializer
    permission_classes = [IsAnyRole]
    filter_backends    = [filters.OrderingFilter]
    ordering_fields    = ['forecast_date', 'predicted_units', 'product_id', 'days_until_stockout']
    ordering           = ['-forecast_date']

    def get_queryset(self):
        queryset   = ProductForecast.objects.select_related('product_ref').all()
        product_id = self.request.query_params.get('product_id')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset


class ProductForecastDetailView(generics.RetrieveAPIView):
    """GET /api/forecasts/<id>/"""
    queryset           = ProductForecast.objects.select_related('product_ref').all()
    serializer_class   = ProductForecastSerializer
    permission_classes = [IsAnyRole]
