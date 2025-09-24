import django_filters
from .models import Product

class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="price",lookup_expr='gte') # Translates to: WHERE price >= min_price
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr='lte') # Translates to: WHERE price <= max_price
    in_stock = django_filters.BooleanFilter(method='filter_in_stock')
    low_stock = django_filters.BooleanFilter(method='filter_low_stock')
    
    class Meta:
        model = Product
        fields = ['category', 'seller', 'is_active', 'is_featured', 'brand']
    
    def filter_in_stock(self,queryset,name,value):
        """filter by stock availablity"""
        if value:
            return queryset.filter(stock_quantity__gt=0)
        return queryset.filter(stock_quantity=0)
    
    def filter_low_stock(self,queryset,name,value):
        """filter by low stock (less that 10 items)"""
        if value:
            return queryset.filter(stock_quantity__lte=10)
        return queryset