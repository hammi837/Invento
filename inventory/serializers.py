from rest_framework import serializers
from .models import Product, ProductForecast


class ProductSerializer(serializers.ModelSerializer):
    needs_reorder = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'product_id',
            'name',
            'category',
            'price',
            'current_stock',
            'reorder_point',
            'needs_reorder',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']


class ProductForecastSerializer(serializers.ModelSerializer):
    # Inline product name so the frontend doesn't need a second request
    product_name = serializers.CharField(source='product_ref.name', read_only=True, default=None)
    category = serializers.CharField(source='product_ref.category', read_only=True, default=None)
    stock_status = serializers.SerializerMethodField()

    class Meta:
        model = ProductForecast
        fields = [
            'id',
            'product_id',
            'product_name',
            'category',
            'forecast_date',
            'predicted_units',
            'current_stock',
            'days_until_stockout',
            'stock_status',
            'generated_at',
        ]

    def get_stock_status(self, obj):
        """
        Traffic-light status based on days of stock remaining.
          critical  — stockout within 7 days
          warning   — stockout within 14 days
          ok        — more than 14 days of stock
          unknown   — no stock data available
        """
        d = obj.days_until_stockout
        if d is None:
            return 'unknown'
        if d <= 7:
            return 'critical'
        if d <= 14:
            return 'warning'
        return 'ok'
