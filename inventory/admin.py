from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Product, ProductForecast, AuditLog


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display  = ('username', 'email', 'role', 'is_active_employee', 'is_staff', 'date_joined')
    list_filter   = ('role', 'is_active_employee', 'is_staff')
    search_fields = ('username', 'email')
    ordering      = ('-date_joined',)
    fieldsets     = BaseUserAdmin.fieldsets + (
        ('Role & Contact', {'fields': ('role', 'phone', 'is_active_employee')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Role & Contact', {'fields': ('role', 'phone')}),
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display   = ('product_id', 'name', 'category', 'current_stock',
                      'reorder_point', 'needs_reorder', 'price', 'is_active')
    list_filter    = ('category', 'is_active')
    search_fields  = ('product_id', 'name')
    ordering       = ('product_id',)
    readonly_fields = ('created_at', 'updated_at')
    list_editable  = ('current_stock', 'reorder_point')

    @admin.display(boolean=True, description='Needs Reorder?')
    def needs_reorder(self, obj):
        return obj.needs_reorder


@admin.register(ProductForecast)
class ProductForecastAdmin(admin.ModelAdmin):
    list_display  = ('product_id', 'forecast_date', 'predicted_units',
                     'current_stock', 'days_until_stockout', 'generated_at')
    list_filter   = ('forecast_date',)
    search_fields = ('product_id',)
    ordering      = ('-forecast_date',)
    readonly_fields = ('generated_at',)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display   = ('user', 'action', 'model_name', 'object_id', 'timestamp')
    list_filter    = ('action', 'model_name', 'timestamp')
    search_fields  = ('object_id', 'details')
    ordering       = ('-timestamp',)
    # Audit logs are immutable — no editing allowed
    readonly_fields = [f.name for f in AuditLog._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
