from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from .models import User, Category, Product, ProductImage, ProductSale, EmailLog
from .serializers import (
    UserRegistrationSerializer, UserProfileSerializer, CategorySerializer,
    ProductListSerializer, ProductDetailSerializer, ProductImageSerializer,
    ProductSaleSerializer, EmailLogSerializer
)
from .utils.email_service import EmailService 
from .utils.notification_service import NotificationService
from .filters import ProductFilter

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
        
        # force CONSUMER role to avoid admin registration
        #TODO implement an admin user invite system instead
        validated_data = serializer.validated_data.copy()
        validated_data['role'] = 'CONSUMER'
        
        # sellers must provide store name
        if request.data.get('role') == 'SELLER':
            if not request.data.get('store_name'):
                return Response(
                    {"store_name": "Store name is required for seller registration!"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            validated_data['role'] = 'SELLER' # allow seller registration
        # create user
        user = serializer.save(**validated_data)
        
        # send welcome email
        EmailService.send_welcome_email(user)
        
        return Response(
            {
                "message": "User registered successfully.",
                "user_id": user.id,
                "username": user.username,
                "role": user.role
            },
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=False,methods=['get','put','patch'])
    @method_decorator(cache_page(60 * 5))
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
    @method_decorator(cache_page(60 * 30))
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
    
    # caching
    @method_decorator(cache_page(60 * 60))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class ProductViewSet(viewsets.ModelViewSet):
    """
    handles product CRUD ops with seller-based permissions
    """
    queryset = Product.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description', 'brand', 'tags']
    ordering_fields = ['price', 'created_at', 'sales_count', 'name']
    ordering = ['-created_at']
    
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
            raise PermissionDenied("Only sellers can create products!")
        serializer.save(seller=self.request.user)
    
    def update(self,request,*args,**kwargs):
        """
        ensure users can only update their own products
        """
        product = self.get_object()
        if product.seller != request.user and not request.user.is_staff:
            raise PermissionDenied("You can only edit your own products!")
        response = super().update(request,*args,**kwargs)
        
        # check for low stock after update
        updated_product = self.get_object()
        NotificationService.check_and_notify_low_stock(updated_product)
        
        return response
    
    @action(detail=True,methods=['post'])
    def record_sale(self,request,pk=None):
        """
        record a product sale
        """
        product = self.get_object()
        
        # Auto-set price_at_sale from product's current price
        initial_data = request.data.copy()
        initial_data['price_at_sale'] = str(product.price)
        
        serializer = ProductSaleSerializer(data=initial_data)
        serializer.is_valid(raise_exception=True)
        
        # create sale record
        sale = serializer.save(
            product=product,
            seller=product.seller,
            buyer=request.user if request.user.is_authenticated else None,
            price_at_sale=product.price
        )
        
        # update product stock and sales count
        product.stock_quantity -=sale.quantity
        product.sales_count +=sale.quantity
        product.save()
        
        # check for low stock after sale
        NotificationService.check_and_notify_low_stock(product)
        
        return Response(
            {
                "message": "Sale recorded successfully.",
                "sale_id": sale.id,
                "remaining_stock": product.stock_quantity
            },
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True,methods=['post'])
    def upload_images(self,request,pk=None):
        """upload multiple images for a product"""
        product = self.get_object()
        
        # permission check
        if product.seller != request.user and not request.user.is_staff:
            raise PermissionDenied("You can only add images to your own products!")
        
        images = request.FILES.getlist('images')
        if not images:
            return Response(
                {"error": "No images provided"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        created_images = []
        for image_file in images:
            image = ProductImage.objects.create(
                product=product,
                image=image_file,
                alt_text=request.data.get('alt_text', f"Image of {product.name}"),
                is_primary=False
            )
            created_images.append(image)
        
        return Response({
            "message": f"Successfully uploaded {len(created_images)} images",
            "images": ProductImageSerializer(created_images, many=True).data
        }, status=status.HTTP_201_CREATED)
    
    #caching
    @method_decorator(cache_page(60 * 15))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @method_decorator(cache_page(60 * 30))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
        
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
            raise PermissionDenied("You can only add images to your own products.")
        
        serializer.save()

class AnalyticsViewSet(viewsets.ViewSet):
    """
    Provides analytics data for sellers and admins.
    """
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    @method_decorator(cache_page(60 * 60))
    def seller_dashboard(self, request):
        """
        Get analytics data for the current seller.
        """
        if not request.user.is_seller:
            raise PermissionDenied("Only sellers can access analytics.")
        
        # sales analytics
        sales_data = ProductSale.objects.filter(seller=request.user).aggregate(
            total_sales=Count('id'),
            total_revenue=Sum('price_at_sale'),
            total_units_sold=Sum('quantity'),
            avg_order_value=Avg('price_at_sale')
        )
        
        # product performance
        top_products = Product.objects.filter(seller=request.user).annotate(
            total_revenue=Sum('sales__price_at_sale'),
            total_units=Sum('sales__quantity')
        ).order_by('-total_revenue')[:5]
        
        # recent sales..last 7 days
        recent_sales = ProductSale.objects.filter(
            seller=request.user,
            sale_date__gte=timezone.now() - timezone.timedelta(days=7)
        ).select_related('product','buyer')
        
        # stock alerts
        low_stock_products = Product.objects.filter(
            seller=request.user,
            stock_quantity__lte=10
        )
        
        return Response({
            'sales_summary': sales_data,
            'top_products': ProductListSerializer(top_products,many=True).data,
            'recent_sales_count': recent_sales.count(),
            'low_stock_alerts': low_stock_products.count(),
            'recent_sales': ProductSaleSerializer(recent_sales,many=True).data
        })
    
    @action(detail=False,methods=['get'])
    def sales_report(self,request):
        """
        Get detail sales report with date filtering
        """
        if not request.user.is_seller:
            raise PermissionDenied("Only sellers can access analytics!")
        
        # date filtering
        days = int(request.query_params.get('days',30)) # 30 days default
        start_date = timezone.now() - timezone.timedelta(days=days)
        
        sales = ProductSale.objects.filter(
            seller=request.user,
            sale_date__gte=start_date
        )
        
        report_data = sales.aggregate(
            total_sales=Count('id'),
            total_revenue=Sum('price_at_sale'),
            average_sale=Avg('price_at_sale'),
            total_units=Sum('quantity')
        )
        
        # daily breakdown
        daily_sales = sales.extra(
            {'sale_day': "date(sale_date)"}
        ).values('sale_day').annotate(
            daily_revenue=Sum('price_at_sale'),
            daily_sales=Count('id')
        ).order_by('sale_day')
        
        return Response({
            'report_period':f'Last {days} days',
            'summary':report_data,
            'daily_breakdown':list(daily_sales)
        })
    
    @action(detail=False,methods=['get'])
    def product_analytics(self,request):
        """
        Get detailed analytics for all seller's products.
        """
        if not request.user.is_seller:
            raise PermissionDenied("Only sellers can access analytics.")
        
        products = Product.objects.filter(seller=request.user).annotate(
            total_revenue=Sum('sales__price_at_sale'),
            total_units_sold=Sum('sales__quantity'),
            sale_count=Count('sales')
        ).order_by('-total_revenue')
    
        return Response({
            'products': ProductListSerializer(products, many=True).data
        })
    
    @action(detail=False,methods=['get'])
    @method_decorator(cache_page(60 * 60))
    def admin_dashboard(self,request):
        """
        system-wide analytics for admins
        """
        if not request.user.is_staff:
            raise PermissionDenied("Only admin users can access this data!")
        
        # platform overview
        platform_data = {
            'total_users': User.objects.count(),
            'total_sellers': User.objects.filter(role='SELLER').count(),
            'total_products': Product.objects.count(),
            'total_sales': ProductSale.objects.count(),
            'total_revenue': ProductSale.objects.aggregate(Sum('price_at_sale'))['price_at_sale__sum'] or 0,
        }
        
        # recent platform activity
        recent_sales = ProductSale.objects.select_related('product','seller','buyer')[:10]
        new_users = User.objects.order_by('-date_joined')[:5]
        
        # seller performance rankings
        top_sellers = User.objects.filter(role='SELLER').annotate(
            total_revenue=Sum('sales_as_seller__price_at_sale'),
            total_sales=Count('sales_as_seller')
        ).order_by('-total_revenue')[:5]
        
        return Response({
            'platform_overview': platform_data,
            'recent_sales': ProductSaleSerializer(recent_sales, many=True).data,
            'recent_users': UserProfileSerializer(new_users, many=True).data,
            'top_sellers': [
                {
                    'username': seller.username,
                    'store_name': seller.store_name,
                    'total_revenue': seller.total_revenue or 0,
                    'total_sales': seller.total_sales or 0
                }
                for seller in top_sellers
            ]
        })
    
    @action(detail=False,methods=['get'])
    def sales_trends(self,request):
        """
        sales trends and growth analytics for admins
        """
        if not request.user.is_staff:
            raise PermissionDenied("Only admin users can access this data.")
        
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timezone.timedelta(days=days)
        
        # daily sales trend
        daily_trends = ProductSale.objects.filter(
            sale_date__gte=start_date
        ).extra({
            'sale_day': "DATE(sale_date)"
        }).values('sale_day').annotate(
            daily_revenue=Sum('price_at_sale'),
            daily_sales=Count('id')
        ).order_by('sale_day')
        
        # category performance
        category_performance = Category.objects.annotate(
            total_revenue=Sum('products__sales__price_at_sale'),
            total_sales=Count('products__sales')
        ).values('name', 'total_revenue', 'total_sales')
        
        return Response({
            'period': f'Last {days} days',
            'daily_trends': list(daily_trends),
            'category_performance': list(category_performance)
        })