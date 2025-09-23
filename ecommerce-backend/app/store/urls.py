from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'users',views.UserViewSet,basename='user')
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'product-images', views.ProductImageViewSet, basename='productimage')

# custom endpoints that don't fit viewset pattern
urlpatterns = [
    path('',include(router.urls)),
    path('analytics/seller-dashboard/', views.AnalyticsViewSet.as_view({'get': 'seller_dashboard'}), name='analytics-dashboard'),
]
router.include_root_view=False