from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    CustomTokenObtainPairView,
    MeView,
    UserViewSet,
    ProductListView,
    ProductDetailView,
    ProductForecastListView,
    ProductForecastDetailView,
)

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')

urlpatterns = [
    # Auth
    path('auth/login/',   CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(),          name='token_refresh'),
    path('auth/me/',      MeView.as_view(),                    name='auth_me'),

    # Users (Admin only — handled by router)
    path('', include(router.urls)),

    # Products
    path('products/',                ProductListView.as_view(),   name='product-list'),
    path('products/<str:product_id>/', ProductDetailView.as_view(), name='product-detail'),

    # Forecasts
    path('forecasts/',          ProductForecastListView.as_view(),   name='forecast-list'),
    path('forecasts/<int:pk>/', ProductForecastDetailView.as_view(), name='forecast-detail'),
]
