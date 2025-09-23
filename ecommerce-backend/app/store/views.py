from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count, Sum
from django.utils import timezone
from .models import User, Category, Product, ProductImage, ProductSale, EmailLog
from .serializers import (
    UserRegistrationSerializer, UserProfileSerializer, CategorySerializer,
    ProductListSerializer, ProductDetailSerializer, ProductImageSerializer,
    ProductSaleSerializer, EmailLogSerializer
)

class UserViewSet(viewsets.ModelViewSet):
    """
    handles user registration,profile management and role-based ops
    """
    queryset = User.objects.all()
    
    def get_serializer_class(self):
        """
        use different serializer based on action
        """
        if self.action == 'create':
            return UserRegistrationSerializer
        return UserProfileSerializer
    
    def get_permissions(self):
        """
        custom permissions based on action
        """
        if self.action == 'create':
            # ofcourse anyone can register
            return [permissions.AllowAny()]
        # other actions require users to be authenticated
        return [permissions.IsAuthenticated()]
    
    def create(self,request,*args,**kwargs):
        """
        user registration with role-based validation
        handles seller store name requirement
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # sellers must provide store name
        if serializer.validated_data.get('role') == 'SELLER':
            if not request.data.get('store_name'):
                return Response(
                    {"store_name": "Store name is required for seller registration!"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        # create user
        user = serializer.save()
        
        # TODO: send welcome email and log the email
        return Response(
            {
                "message": "User registered successfully.",
                "user_id": user.id,
                "username":user.username
            },
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=False,methods=['get','put','patch'])
    def me(self,request):
        """
        Get or update user's profile
        """
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        
        # update profile
        serializer = self.get_serializer(
            request.user,
            data=request.data,
            partial=True  #allow partial updates
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data)

class CategoryViewSet(viewsets.ModelViewSet):
    """
    handes category CRUD ops with hierarchichal support
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        """
        optimize queryset with prefetch_related for performance.
        """
        queryset = Category.objects.prefetch_related('subcategories','products')
        
        # filter active categories for non-staff users
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True)
        
        return queryset
    
    @action(detail=True,methods=['get'])
    def products(self,request,pk=None):
        """
        get all products in a specific category including subcategories
        """
        category = self.get_object()
        
        # Get all subcategories including nested
        def get_all_subcategories(cat):
            subcategories = list(cat.subcategories.all())
            for subcat in cat.subcategories.all():
                subcategories.extend(get_all_subcategories(subcat))
            return subcategories
        
        all_categories = [category] + get_all_subcategories(category)
        
        # get products from all categories
        products = Product.objects.filter(
            category__in=all_categories,
            is_active=True
        ).select_related('seller','category')
        
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = ProductListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)

class ProductViewSet(viewsets.ModelViewSet):
    """
    handles product CRUD ops with seller-based permissions
    """
    queryset = Product.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        """
        use detail serializer for retrieve,use list serializer for list
        """
        if self.action == "retrieve":
            return ProductDetailSerializer
        return ProductListSerializer
    
    def get_queryset(self):
        """
        optimize queryset and apply filters
        """
        queryset = Product.objects.select_related('seller','category')\
                                  .prefetch_related('images')
        
        # apply filters
        category = self.request.query_params.get('category')
        seller = self.request.query_params.get('seller')
        featured = self.request.query_params.get('featured')
        
        if category:
            queryset = queryset.filter(category_id=category)
        if seller:
            queryset = queryset.filter(seller_id=seller)
        if featured and featured.lower() == 'true':
            queryset = queryset.filter(is_featured=True)
        
        # only show active products to non-owners
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True)
        return queryset
    
    def perform_create(self,serializer):
        """
        automatically set the seller to the current user
        """
        # ensure only sellers can create products
        if not self.request.user.is_seller:
            raise permissions.PermissionDenied("Only sellers can create products!")
        serializer.save(seller=self.request.user)
    
    def update(self,request,*args,**kwargs):
        """
        ensure users can only update their own products
        """
        product = self.get_object()
        if product.seller != request.user and not request.user.is_staff:
            raise permissions.PermissionDenied("You can only edit your own products!")
        return super().update(request,*args,**kwargs)
    
    @action(detail=True,methods=['post'])
    def record_sale(self,request,pk=None):
        """
        record a product sale
        """
        product = self.get_object()
        serializer = ProductSaleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # create sale record
        sale = serializer.save(
            product=product,
            seller=product.seller,
            buyer=request.user if request.user.is_authenticated else None
        )
        
        # update product stock and sales count
        product.stock_quantity -=sale.quantity
        product.sales_count +=sale.quantity
        product.save()
        
        return Response(
            {
                "message": "Sale recorded successfully.",
                "sale_id": sale.id,
                "remaining_stock": product.stock_quantity
            },
            status=status.HTTP_201_CREATED
        )

class ProductImageViewSet(viewsets.ModelViewSet):
    """
    Handles product image operations.
    """
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """
        Filter images by product if product_id is provided.
        """
        queryset = ProductImage.objects.all()
        product_id = self.request.query_params.get('product_id')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset

    def perform_create(self, serializer):
        """
        Verify user owns the product before adding images.
        """
        product = serializer.validated_data['product']
        if product.seller != self.request.user and not self.request.user.is_staff:
            raise permissions.PermissionDenied("You can only add images to your own products.")
        
        serializer.save()

class AnalyticsViewSet(viewsets.ViewSet):
    """
    Provides analytics data for sellers and admins.
    """
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def seller_dashboard(self, request):
        """
        Get analytics data for the current seller.
        """
        if not request.user.is_seller:
            raise permissions.PermissionDenied("Only sellers can access analytics.")
        
        # Basic sales analytics
        sales_data = ProductSale.objects.filter(seller=request.user).aggregate(
            total_sales=Count('id'),
            total_revenue=Sum('price_at_sale'),
            total_units_sold=Sum('quantity')
        )
        
        # Recent sales
        recent_sales = ProductSale.objects.filter(seller=request.user)\
                                         .select_related('product', 'buyer')[:10]
        
        return Response({
            'sales_summary': sales_data,
            'recent_sales': ProductSaleSerializer(recent_sales, many=True).data
        })
