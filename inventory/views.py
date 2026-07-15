from rest_framework import generics, filters
from rest_framework.permissions import AllowAny
from .models import ProductForecast
from .serializers import ProductForecastSerializer


class ProductForecastListView(generics.ListAPIView):
    """
    GET /api/forecasts/
    Returns all forecasts. Supports filtering by product_id and ordering.

    Query params:
      ?product_id=P0001       — filter by a specific product
      ?ordering=forecast_date — sort ascending by date
    """
    serializer_class = ProductForecastSerializer
    permission_classes = [AllowAny]  # Open for now — lock down before production
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['forecast_date', 'predicted_units', 'product_id']
    ordering = ['-forecast_date']

    def get_queryset(self):
        queryset = ProductForecast.objects.all()
        product_id = self.request.query_params.get('product_id')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset


class ProductForecastDetailView(generics.RetrieveAPIView):
    """
    GET /api/forecasts/<id>/
    Returns a single forecast record by primary key.
    """
    queryset = ProductForecast.objects.all()
    serializer_class = ProductForecastSerializer
    permission_classes = [AllowAny]
