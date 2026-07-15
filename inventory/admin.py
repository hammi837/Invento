from django.contrib import admin
from .models import ProductForecast


@admin.register(ProductForecast)
class ProductForecastAdmin(admin.ModelAdmin):
    list_display = ('product_id', 'forecast_date', 'predicted_units', 'current_stock', 'days_until_stockout', 'generated_at')
    list_filter = ('forecast_date',)
    search_fields = ('product_id',)
    ordering = ('-forecast_date',)
    readonly_fields = ('generated_at',)
