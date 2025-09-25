from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, Category, Product, ProductImage, ProductSale, EmailLog

class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    handles user registration with password and role-based validation
    separated from profile serializer for security
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'},
        help_text="Password must meet security requirements"
    )
    # confirmation password
    password2 = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text="Enter the same password for confirmation"
    )
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password2', 'role',
            'first_name', 'last_name', 'phone_number'
        ]
        extra_kwargs = {
            'password':{'write_only':True},
            'email':{'required':True}
        }
    
    def validate(self,attrs):
        """
        validate passwords match and seller has a store name
        """
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password":"Password fields didn't match!"}
            )
        
        # remove password2 from attributes since it isn't a field on our model
        attrs.pop('password2')
        
        # sellers must register with their store name,i will handle this in views hopefully lol
        return attrs
    
    def create(self,validated_data):
        """
        create user with hashed password
        """
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    """
    handles user profile updates except sensitive fields eg passwords
    Read-only fields
    """
    role = serializers.CharField(read_only=True)  # users can't change roles
    is_email_verified = serializers.BooleanField(read_only=True)
    profile_picture = serializers.ImageField(required=False, allow_null=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'role',
            'phone_number', 'address', 'store_name', 'profile_picture',
            'is_email_verified', 'is_active', 'date_joined', 'created_at'
        ]
        read_only_fields = ['id','username','date_joined','created_at']

class CategorySerializer(serializers.ModelSerializer):
    """
    category serialization with hierachichal support
    includes parent category info and subcategories count
    """
    subcategories_count = serializers.IntegerField(
        source='subcategories.count',
        read_only=True,
        help_text="Number of direct subcategories"
    )
    products_count = serializers.IntegerField(
        source='products.count', 
        read_only=True,
        help_text="Number of products in this category"
    )
    parent_category_name = serializers.CharField(
        source='parent_category.name',
        read_only=True,
        help_text="Name of parent category for easy display"
    )
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'description', 'slug', 'parent_category',
            'parent_category_name', 'is_active', 'subcategories_count',
            'products_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at']
        
    def validate_parent_category(self,value):
        """
        prevent circular category relationships
        """
        if value and value == self.instance:
            raise serializers.ValidationError("Category cannot be its own parent")
        return value

class ProductImageSerializer(serializers.ModelSerializer):
    """
    handle product image serialization with primary image validation
    """
    image = serializers.ImageField(required=True)
    
    class Meta:
        model = ProductImage
        fields = ['id', 'product', 'image', 'alt_text', 'is_primary', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def validate(self,attrs):
        """
        ensure only one primary image per product
        """
        if attrs.get('is_primary'):
            product = attrs.get('product') or self.instance.product if self.instance else None
            if product:
                existing_primary = ProductImage.objects.filter(
                    product=product,
                    is_primary=True
                ).exclude(pk=self.instance.pk if self.instance else None)
                
                if existing_primary.exists():
                    raise serializers.ValidationError(
                        {"is_primary": "This product already has a primary image."}
                    )
        return attrs

class ProductListSerializer(serializers.ModelSerializer):
    """
    Optimized serializer for product listings (fewer fields for performance).
    Includes essential related data for display in lists.
    """
    seller = serializers.PrimaryKeyRelatedField(read_only=True)
    seller_name = serializers.CharField(source='seller.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    primary_image = serializers.SerializerMethodField()
    is_in_stock = serializers.BooleanField(read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'price', 'sku', 'category', 'category_name',
            'seller', 'seller_name', 'stock_quantity', 'is_active',
            'is_featured', 'sales_count', 'brand', 'is_in_stock',
            'is_low_stock', 'primary_image', 'created_at'
        ]
        read_only_fields = ['sales_count', 'created_at','seller',]

    def get_primary_image(self, obj):
        """Get the primary product image URL if available"""
        primary_image = obj.images.filter(is_primary=True).first()
        return primary_image.image if primary_image else None

class ProductDetailSerializer(ProductListSerializer):
    """
    serializer for individual product views.
    Includes all images and full product details.
    """
    images = ProductImageSerializer(many=True, read_only=True)
    seller_store = serializers.CharField(source='seller.store_name', read_only=True)

    class Meta(ProductListSerializer.Meta):
        fields = ProductListSerializer.Meta.fields + [
            'description', 'tags', 'images', 'seller_store', 'updated_at'
        ]
        read_only_fields = ProductListSerializer.Meta.read_only_fields + ['updated_at']

class ProductSaleSerializer(serializers.ModelSerializer):
    """
    Handles product sale recording with price validation.
    Includes related product and buyer information.
    """
    product = serializers.PrimaryKeyRelatedField(read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    seller = serializers.PrimaryKeyRelatedField(read_only=True)
    seller_name = serializers.CharField(source='seller.username', read_only=True)
    buyer_name = serializers.CharField(source='buyer.username', read_only=True)
    price_at_sale = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_amount = serializers.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        read_only=True,
        help_text="Total sale amount (quantity × price)"
    )

    class Meta:
        model = ProductSale
        fields = [
            'id', 'product', 'product_name', 'seller', 'seller_name',
            'buyer', 'buyer_name', 'quantity', 'price_at_sale', 'total_amount',
            'sale_date'
        ]
        read_only_fields = ['id', 'sale_date', 'seller', 'product','price_at_sale']
    
    def validate(self,attrs):
        """
        validate sale data including stock availability
        """
        product = attrs.get('product')
        quantity = attrs.get('quantity')
        
        if product and quantity:
            if quantity > product.stock_quantity:
                raise serializers.ValidationError(
                    {"quantity": f"Only {product.stock_quantity} items available in stock"}
                )
            # set price_at_sale to current product price if not provided
            if not attrs.get('price_at_sale'):
                attrs['price_at_sale'] = product.price
            
        return attrs

class EmailLogSerializer(serializers.ModelSerializer):
    """
    Handles email log serialization for tracking and analytics.
    Mostly read-only as emails are system-generated.
    """
    recipient_username = serializers.CharField(
        source='recipient_user.username', 
        read_only=True,
        help_text="Username of recipient if registered"
    )

    class Meta:
        model = EmailLog
        fields = [
            'id', 'recipient_email', 'recipient_user', 'recipient_username',
            'email_type', 'subject', 'status', 'sent_at', 'error_message',
            'created_at'
        ]
        read_only_fields = ['id', 'sent_at', 'created_at']