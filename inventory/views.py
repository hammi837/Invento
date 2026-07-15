from rest_framework import generics, filters, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django_filters.rest_framework import DjangoFilterBackend

from .models import Product, ProductForecast, AuditLog, User
from .serializers import ProductSerializer, ProductForecastSerializer, AuditLogSerializer
from .auth_serializers import (
    CustomTokenObtainPairSerializer,
    UserSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    MeSerializer,
)
from .permissions import IsAdmin, IsManagerOrAdmin, IsAnyRole, ReadOnlyOrManagerAbove


# ─────────────────────────────────────────────
# Auth
# ─────────────────────────────────────────────

class CustomTokenObtainPairView(TokenObtainPairView):
    """POST /api/auth/login/"""
    serializer_class = CustomTokenObtainPairSerializer


class MeView(APIView):
    """GET /api/auth/me/"""
    permission_classes = [IsAnyRole]

    def get(self, request):
        return Response(MeSerializer(request.user).data)


# ─────────────────────────────────────────────
# User management (Admin only)
# ─────────────────────────────────────────────

class UserViewSet(viewsets.ModelViewSet):
    """
    Admin-only CRUD on users.
    GET    /api/users/           list
    POST   /api/users/           create
    GET    /api/users/<id>/      retrieve
    PATCH  /api/users/<id>/      update
    DELETE /api/users/<id>/      deactivate (soft)
    POST   /api/users/<id>/deactivate/  toggle active
    """
    queryset           = User.objects.all().order_by('date_joined')
    permission_classes = [IsAdmin]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        if self.action in ('update', 'partial_update'):
            return UserUpdateSerializer
        return UserSerializer

    def destroy(self, request, *args, **kwargs):
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
# Products (Phase 2 — full CRUD + audit log)
# ─────────────────────────────────────────────

class ProductViewSet(viewsets.ModelViewSet):
    """
    GET    /api/products/           list    (all roles)
    POST   /api/products/           create  (manager / admin)
    GET    /api/products/<id>/      detail  (all roles)
    PATCH  /api/products/<id>/      update  (manager / admin)
    DELETE /api/products/<id>/      delete  (admin only)

    Filters:  ?category=electronics
    Search:   ?search=laptop
    Ordering: ?ordering=current_stock
    """
    queryset           = Product.objects.all().order_by('product_id')
    serializer_class   = ProductSerializer
    permission_classes = [ReadOnlyOrManagerAbove]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields   = ['category', 'is_active']
    search_fields      = ['name', 'product_id']
    ordering_fields    = ['product_id', 'current_stock', 'price', 'name']

    def perform_create(self, serializer):
        instance = serializer.save()
        AuditLog.objects.create(
            user=self.request.user,
            action=AuditLog.Action.CREATE,
            model_name='Product',
            object_id=instance.product_id,
            details=f"Created '{instance.name}' — stock: {instance.current_stock}",
        )

    def perform_update(self, serializer):
        instance = serializer.save()
        AuditLog.objects.create(
            user=self.request.user,
            action=AuditLog.Action.UPDATE,
            model_name='Product',
            object_id=instance.product_id,
            details=f"Updated '{instance.name}' — stock: {instance.current_stock}, price: {instance.price}",
        )

    def perform_destroy(self, instance):
        AuditLog.objects.create(
            user=self.request.user,
            action=AuditLog.Action.DELETE,
            model_name='Product',
            object_id=instance.product_id,
            details=f"Deleted '{instance.name}'",
        )
        instance.delete()

    def destroy(self, request, *args, **kwargs):
        if request.user.role != 'admin':
            return Response(
                {'detail': 'Only admins can delete products.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)


# ─────────────────────────────────────────────
# Audit log (Manager / Admin read-only)
# ─────────────────────────────────────────────

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/audit-logs/        list  (manager / admin)
    GET /api/audit-logs/<id>/   detail

    Filters:  ?action=create  ?model_name=Product
    Ordering: ?ordering=-timestamp
    """
    queryset           = AuditLog.objects.select_related('user').all()
    serializer_class   = AuditLogSerializer
    permission_classes = [IsManagerOrAdmin]
    filter_backends    = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields   = ['action', 'model_name']
    ordering_fields    = ['timestamp']
    ordering           = ['-timestamp']


# ─────────────────────────────────────────────
# Forecasts
# ─────────────────────────────────────────────

class ProductForecastListView(generics.ListAPIView):
    """GET /api/forecasts/  — all roles."""
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
