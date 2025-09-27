from django.contrib import admin
from django.urls import path,include
from django.urls import re_path
from django.http import JsonResponse
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# setup automatic docs generator
schema_view = get_schema_view(
    openapi.Info(
        title="Alx E-Commerce API",
        default_version='v1',
        descriptiom="Role-based E-commerce API",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="njugunabriian.dev@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

def root_handler(request):
    return JsonResponse({
        "message": "ALX-Project-Nexus-E-Commerce API", 
        "version": "1.0",
        "documentation": "/swagger/",
        "status": "active"
    })
    
urlpatterns = [
    path('', root_handler),
    path('admin/', admin.site.urls),
    path('api/v1/',include('store.urls')),
    
    # api documentation endpoints
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'), # JSON data of API structure
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'), # interactive docs
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'), # read-only docs
]
