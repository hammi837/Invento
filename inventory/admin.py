from django.contrib import admin
from .models import Product, ProductForecast


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_id', 'name', 'category', 'current_stock', 'reorder_point', 'needs_reorder', 'price', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('product_id', 'name')
    ordering = ('product_id',)
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('current_stock', 'reorder_point')

    @admin.display(boolean=True, description='Needs Reorder?')
    def needs_reorder(self, obj):
        return obj.needs_reorder


@admin.register(ProductForecast)
class ProductForecastAdmin(admin.ModelAdmin):
    list_display = ('product_id', 'forecast_date', 'predicted_units', 'current_stock', 'days_until_stockout', 'generated_at')
    list_filter = ('forecast_date',)
    search_fields = ('product_id',)
    ordering = ('-forecast_date',)
    readonly_fields = ('generated_at',)
