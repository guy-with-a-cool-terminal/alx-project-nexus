from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

router = DefaultRouter()
router.register(r'users',views.UserViewSet,basename='user')
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'product-images', views.ProductImageViewSet, basename='productimage')

# endpoints that don't fit viewset pattern
urlpatterns = [
    path('auth/login/',TokenObtainPairView.as_view(),name='token_obtain_pair'),
    path('auth/refresh/',TokenRefreshView.as_view(),name='token_refresh'),
    path('products/<int:pk>/upload-images/', views.ProductViewSet.as_view({'post': 'upload_images'}), name='product-upload-images'),
    path('analytics/sales-report/', views.AnalyticsViewSet.as_view({'get': 'sales_report'}), name='analytics-sales-report'),
    path('analytics/product-analytics/', views.AnalyticsViewSet.as_view({'get': 'product_analytics'}), name='analytics-products'),
    path('analytics/seller-dashboard/', views.AnalyticsViewSet.as_view({'get': 'seller_dashboard'}), name='analytics-dashboard'),
    path('analytics/admin-dashboard/', views.AnalyticsViewSet.as_view({'get': 'admin_dashboard'}), name='admin-dashboard'),
    path('analytics/sales-trends/', views.AnalyticsViewSet.as_view({'get': 'sales_trends'}), name='sales-trends'),
    path('',include(router.urls)),
]
router.include_root_view=False