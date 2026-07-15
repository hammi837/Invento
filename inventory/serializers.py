from rest_framework import serializers
from .models import ProductForecast


class ProductForecastSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductForecast
        fields = [
            'id',
            'product_id',
            'forecast_date',
            'predicted_units',
            'current_stock',
            'days_until_stockout',
            'generated_at',
        ]
