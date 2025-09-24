class ProductViewSet(viewsets.ModelViewSet):
    """
    handles product CRUD ops with seller-based permissions
    """
    queryset = Product.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    # MOVE THESE LINES HERE (proper indentation):
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description', 'brand', 'tags']
    ordering_fields = ['price', 'created_at', 'sales_count', 'name']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        # ... rest of your code stays the same ...