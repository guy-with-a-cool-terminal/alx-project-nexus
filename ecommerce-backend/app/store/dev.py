from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

class ProductViewSet(viewsets.ModelViewSet):
    # ... your existing code ...
    
    # ADD THESE LINES
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'seller', 'is_active', 'is_featured', 'brand']
    search_fields = ['name', 'description', 'brand', 'tags']
    ordering_fields = ['price', 'created_at', 'sales_count', 'name']
    ordering = ['-created_at']  # default ordering