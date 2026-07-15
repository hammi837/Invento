from rest_framework import serializers
from .models import Product, ProductForecast, AuditLog


class ProductSerializer(serializers.ModelSerializer):
    needs_reorder = serializers.BooleanField(read_only=True)

    class Meta:
        model  = Product
        fields = [
            'id', 'product_id', 'name', 'category', 'price',
            'current_stock', 'reorder_point', 'needs_reorder',
            'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_current_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock cannot be negative.")
        return value

    def validate_price(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value

    def validate_reorder_point(self, value):
        if value < 0:
            raise serializers.ValidationError("Reorder point cannot be negative.")
        return value


class ProductForecastSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product_ref.name', read_only=True, default=None)
    category     = serializers.CharField(source='product_ref.category', read_only=True, default=None)
    stock_status = serializers.SerializerMethodField()

    class Meta:
        model  = ProductForecast
        fields = [
            'id', 'product_id', 'product_name', 'category',
            'forecast_date', 'predicted_units', 'current_stock',
            'days_until_stockout', 'stock_status', 'generated_at',
        ]

    def get_stock_status(self, obj):
        d = obj.days_until_stockout
        if d is None:
            return 'unknown'
        if d <= 7:
            return 'critical'
        if d <= 14:
            return 'warning'
        return 'ok'


class AuditLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True, default=None)

    class Meta:
        model  = AuditLog
        fields = [
            'id', 'username', 'action', 'model_name',
            'object_id', 'details', 'timestamp',
        ]
        read_only_fields = fields
