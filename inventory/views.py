from rest_framework import generics, filters
from rest_framework.permissions import AllowAny
from .models import Product, ProductForecast
from .serializers import ProductSerializer, ProductForecastSerializer


class ProductListView(generics.ListAPIView):
    """
    GET /api/products/
    Returns all active products with current stock levels.

    Query params:
      ?category=electronics   — filter by category
      ?needs_reorder=true     — show only products below reorder point
      ?ordering=current_stock — sort by stock level
    """
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['product_id', 'current_stock', 'name', 'category']
    search_fields = ['product_id', 'name']
    ordering = ['product_id']

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)
        category = self.request.query_params.get('category')
        needs_reorder = self.request.query_params.get('needs_reorder')
        if category:
            queryset = queryset.filter(category=category)
        if needs_reorder and needs_reorder.lower() == 'true':
            # Filter products where current_stock <= reorder_point
            from django.db.models import F
            queryset = queryset.filter(current_stock__lte=F('reorder_point'))
        return queryset


class ProductDetailView(generics.RetrieveUpdateAPIView):
    """
    GET  /api/products/<product_id>/   — retrieve a product
    PATCH /api/products/<product_id>/  — update stock level or reorder point
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    lookup_field = 'product_id'


class ProductForecastListView(generics.ListAPIView):
    """
    GET /api/forecasts/
    Returns demand forecasts with stock status.

    Query params:
      ?product_id=P0001            — filter by product
      ?stock_status=critical       — critical | warning | ok | unknown
      ?ordering=-predicted_units   — sort by demand descending
    """
    serializer_class = ProductForecastSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['forecast_date', 'predicted_units', 'product_id', 'days_until_stockout']
    ordering = ['-forecast_date']

    def get_queryset(self):
        queryset = ProductForecast.objects.select_related('product_ref').all()
        product_id = self.request.query_params.get('product_id')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset


class ProductForecastDetailView(generics.RetrieveAPIView):
    """
    GET /api/forecasts/<id>/
    Single forecast record.
    """
    queryset = ProductForecast.objects.select_related('product_ref').all()
    serializer_class = ProductForecastSerializer
    permission_classes = [AllowAny]
