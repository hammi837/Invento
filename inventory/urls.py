from django.urls import path
from .views import ProductForecastListView, ProductForecastDetailView

urlpatterns = [
    path('forecasts/', ProductForecastListView.as_view(), name='forecast-list'),
    path('forecasts/<int:pk>/', ProductForecastDetailView.as_view(), name='forecast-detail'),
]
