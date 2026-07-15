from django.urls import path
from .views import (
    ProductListView,
    ProductDetailView,
    ProductForecastListView,
    ProductForecastDetailView,
)

urlpatterns = [
    # Products
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/<str:product_id>/', ProductDetailView.as_view(), name='product-detail'),

    # Forecasts
    path('forecasts/', ProductForecastListView.as_view(), name='forecast-list'),
    path('forecasts/<int:pk>/', ProductForecastDetailView.as_view(), name='forecast-detail'),
]
