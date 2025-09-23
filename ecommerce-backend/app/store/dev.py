from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator, MinValueValidator
from decimal import Decimal


class User(AbstractUser):
    """
    Custom user model that extends Django's AbstractUser.
    Supports multi-role system: Sellers can create products, Consumers browse/buy,
    Admins manage the entire system.
    """
    
    # Define the three roles our system supports
    ROLE_CHOICES = [
        ('SELLER', 'Seller'),
        ('CONSUMER', 'Consumer'), 
        ('ADMIN', 'Admin'),
    ]
    
    # Core role field that determines user permissions throughout the app
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='CONSUMER',
        help_text="User role determines access permissions"
    )
    
    # Contact information - phone with validation regex
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Phone number must be entered in format: '+999999999'. Up to 15 digits allowed."
        )]
    )
    
    # Address stored as text for flexibility (street, city, state, zip combined)
    address = models.TextField(
        blank=True,
        null=True,
        help_text="Full address for business/shipping purposes"
    )
    
    # Store name - only relevant for sellers but stored on all users for simplicity
    store_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Store name for seller identification"
    )
    
    # Profile picture URL from Cloudinary (not file upload to avoid storage complexity)
    profile_picture = models.CharField(
        max_length=500,  # URLs can be long
        blank=True,
        null=True,
        help_text="Profile image URL from Cloudinary"
    )
    
    # Email verification status for security
    is_email_verified = models.BooleanField(
        default=False,
        help_text="Email verification status"
    )
    
    # Automatic timestamps for auditing
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        """String representation shows username and role for admin interface"""
        return f"{self.username} ({self.get_role_display()})"
    
    # Convenience properties to check user roles without string comparison
    @property
    def is_seller(self):
        """Check if user is a seller"""
        return self.role == 'SELLER'
    
    @property 
    def is_consumer(self):
        """Check if user is a consumer"""
        return self.role == 'CONSUMER'
    
    @property
    def is_admin_user(self):
        """Check if user is admin (avoid conflict with Django's is_admin)"""
        return self.role == 'ADMIN'


class Category(models.Model):
    """
    Product categories with hierarchical structure.
    Supports nested categories (parent-child relationships).
    Example: Electronics > Phones > Smartphones
    """
    
    # Category name - keep it concise for URLs and navigation
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Category name (must be unique)"
    )
    
    # Detailed description for SEO and user understanding
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Detailed category description"
    )
    
    # URL-friendly version of name (auto-generated in save method or admin)
    slug = models.SlugField(
        max_length=100,
        unique=True,
        help_text="URL-friendly version of category name"
    )
    
    # Self-referencing foreign key for hierarchical structure
    parent_category = models.ForeignKey(
        'self',  # Reference to same model
        on_delete=models.CASCADE,  # Delete children when parent deleted
        null=True,
        blank=True,
        related_name='subcategories',  # Access children via parent.subcategories.all()
        help_text="Parent category for hierarchical organization"
    )
    
    # Active/inactive status for category management
    is_active = models.BooleanField(
        default=True,
        help_text="Whether category is active and visible"
    )
    
    # Timestamps for auditing
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        # Ensure categories are ordered alphabetically by default
        ordering = ['name']
    
    def __str__(self):
        """String representation shows full category path"""
        if self.parent_category:
            return f"{self.parent_category.name} > {self.name}"
        return self.name
    
    def get_full_path(self):
        """Returns full category path as list for breadcrumbs"""
        path = [self.name]
        parent = self.parent_category
        while parent:
            path.insert(0, parent.name)
            parent = parent.parent_category
        return path


class Product(models.Model):
    """
    Main product model containing all product information.
    Each product belongs to one seller and one category.
    Tracks inventory and sales for analytics.
    """
    
    # Basic product information
    name = models.CharField(
        max_length=200,
        help_text="Product name/title"
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Detailed product description"
    )
    
    # Price with decimal precision for currency
    price = models.DecimalField(
        max_digits=10,  # Up to 99,999,999.99
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],  # Minimum 1 cent
        help_text="Product price"
    )
    
    # Unique product identifier for inventory management
    sku = models.CharField(
        max_length=100,
        unique=True,
        help_text="Stock Keeping Unit - unique product identifier"
    )
    
    # Foreign key relationships
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,  # Delete products when category deleted
        related_name='products',  # Access via category.products.all()
        help_text="Product category"
    )
    
    seller = models.ForeignKey(
        User,
        on_delete=models.CASCADE,  # Delete products when seller account deleted
        related_name='products',  # Access via user.products.all()
        limit_choices_to={'role': 'SELLER'},  # Only sellers can own products
        help_text="Product seller"
    )
    
    # Inventory management
    stock_quantity = models.PositiveIntegerField(
        default=0,
        help_text="Current stock quantity"
    )
    
    # Product status flags
    is_active = models.BooleanField(
        default=True,
        help_text="Whether product is active and visible"
    )
    
    is_featured = models.BooleanField(
        default=False,
        help_text="Whether product is featured on homepage"
    )
    
    # Analytics field - incremented with each sale
    sales_count = models.PositiveIntegerField(
        default=0,
        help_text="Total number of times this product has been sold"
    )
    
    # Additional product attributes
    brand = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Product brand"
    )
    
    tags = models.TextField(
        blank=True,
        null=True,
        help_text="Comma-separated tags for search and filtering"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'products'
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        # Default ordering by creation date (newest first)
        ordering = ['-created_at']
        # Database indexes for performance on commonly queried fields
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['seller']),
            models.Index(fields=['is_active']),
            models.Index(fields=['price']),
        ]
    
    def __str__(self):
        """String representation shows product name and seller"""
        return f"{self.name} by {self.seller.username}"
    
    @property
    def is_in_stock(self):
        """Check if product has stock available"""
        return self.stock_quantity > 0
    
    @property
    def is_low_stock(self, threshold=10):
        """Check if product is low on stock (default threshold: 10)"""
        return self.stock_quantity <= threshold


class ProductImage(models.Model):
    """
    Product images with support for multiple images per product.
    One image can be marked as primary for listings.
    """
    
    # Foreign key to product
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,  # Delete images when product deleted
        related_name='images',  # Access via product.images.all()
        help_text="Associated product"
    )
    
    # Image URL from Cloudinary (not file upload)
    image = models.CharField(
        max_length=500,
        help_text="Image URL from Cloudinary"
    )
    
    # Alt text for accessibility and SEO
    alt_text = models.CharField(
        max_length=255,
        help_text="Alternative text for image accessibility"
    )
    
    # Mark one image as primary for product listings
    is_primary = models.BooleanField(
        default=False,
        help_text="Whether this is the primary product image"
    )
    
    # Timestamp for ordering images
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'product_images'
        verbose_name = 'Product Image'
        verbose_name_plural = 'Product Images'
        # Order images with primary first, then by creation date
        ordering = ['-is_primary', 'created_at']
    
    def __str__(self):
        """String representation shows product name and primary status"""
        primary_text = " (Primary)" if self.is_primary else ""
        return f"Image for {self.product.name}{primary_text}"


class ProductSale(models.Model):
    """
    Track individual product sales for analytics.
    Records who bought what, when, and at what price.
    """
    
    # Foreign key to product
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,  # Delete sales records when product deleted
        related_name='sales',  # Access via product.sales.all()
        help_text="Product that was sold"
    )
    
    # Foreign key to seller (for quick seller analytics queries)
    seller = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sales_as_seller',
        limit_choices_to={'role': 'SELLER'},
        help_text="Seller of the product"
    )
    
    # Foreign key to buyer (optional - for registered users only)
    buyer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,  # Keep sale record even if buyer deleted
        null=True,
        blank=True,
        related_name='purchases',
        help_text="Buyer of the product (if registered user)"
    )
    
    # Sale details
    quantity = models.PositiveIntegerField(
        default=1,
        help_text="Quantity sold"
    )
    
    # Price at time of sale (important for analytics - prices change over time)
    price_at_sale = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price per unit at time of sale"
    )
    
    # When the sale occurred
    sale_date = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time of sale"
    )
    
    class Meta:
        db_table = 'product_sales'
        verbose_name = 'Product Sale'
        verbose_name_plural = 'Product Sales'
        # Order sales by date (newest first)
        ordering = ['-sale_date']
        # Database indexes for analytics queries
        indexes = [
            models.Index(fields=['seller']),
            models.Index(fields=['product']),
            models.Index(fields=['sale_date']),
        ]
    
    def __str__(self):
        """String representation shows sale summary"""
        return f"{self.quantity}x {self.product.name} sold on {self.sale_date.date()}"
    
    @property
    def total_amount(self):
        """Calculate total sale amount"""
        return self.quantity * self.price_at_sale


class EmailLog(models.Model):
    """
    Track all emails sent by the system for debugging and analytics.
    Records delivery status and error messages.
    """
    
    # Email types our system sends
    EMAIL_TYPE_CHOICES = [
        ('WELCOME', 'Welcome Email'),
        ('ANALYTICS_REPORT', 'Analytics Report'),
        ('LOW_STOCK_ALERT', 'Low Stock Alert'),
        ('SYSTEM_NOTIFICATION', 'System Notification'),
    ]
    
    # Email delivery status
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SENT', 'Sent Successfully'),
        ('FAILED', 'Failed to Send'),
        ('BOUNCED', 'Bounced'),
    ]
    
    # Email details
    recipient_email = models.EmailField(
        help_text="Email address of recipient"
    )
    
    # Link to user if they're registered (for analytics)
    recipient_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='received_emails',
        help_text="Recipient user (if registered)"
    )
    
    # Email categorization
    email_type = models.CharField(
        max_length=50,
        choices=EMAIL_TYPE_CHOICES,
        help_text="Type of email sent"
    )
    
    # Email content summary
    subject = models.CharField(
        max_length=255,
        help_text="Email subject line"
    )
    
    # Delivery tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        help_text="Email delivery status"
    )
    
    # Timestamp when email was sent (or attempted)
    sent_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When email was sent/attempted"
    )
    
    # Error message if sending failed
    error_message = models.TextField(
        blank=True,
        null=True,
        help_text="Error message if email failed to send"
    )
    
    # Timestamp for record keeping
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'email_logs'
        verbose_name = 'Email Log'
        verbose_name_plural = 'Email Logs'
        # Order by send date (newest first)
        ordering = ['-sent_at']
        # Indexes for analytics and filtering
        indexes = [
            models.Index(fields=['recipient_user']),
            models.Index(fields=['email_type']),
            models.Index(fields=['status']),
            models.Index(fields=['sent_at']),
        ]
    
    def __str__(self):
        """String representation shows email summary"""
        return f"{self.email_type} to {self.recipient_email} - {self.status}"