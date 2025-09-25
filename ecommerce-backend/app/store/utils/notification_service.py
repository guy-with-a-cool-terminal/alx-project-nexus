from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
from ..models import EmailLog, Product, ProductSale

class NotificationService:
    @staticmethod
    def send_low_stock_alerts(seller):
        """send low stock alerts to seller for all their products"""
        low_stock_products = Product.objects.filter(
            seller=seller,
            stock_quantity__lte=10,
            is_active=True
        )
        
        if not low_stock_products.exists():
            return False
        
        subject = 'Low Stock Alert - Action Required'
        product_list = '\n'.join([
            f"- {product.name}: {product.stock_quantity} left (SKU: {product.sku})"
            for product in low_stock_products
        ])
        
        message = f'''
        Hi {seller.username},
        
        The following products are running low on stock:
        
        {product_list}
        
        Please consider restocking to avoid missed sales opportunities.
        
        Best regards,
        Your E-Commerce Platform
        '''
        
        try:
            send_mail(
                subject,
                message.strip(),
                settings.DEFAULT_FROM_EMAIL,
                [seller.email],
                fail_silently=False,
            )
            EmailLog.objects.create(
                recipient_email=seller.email,
                recipient_user=seller,
                email_type='LOW_STOCK_ALERT',
                subject=subject,
                status='SENT'
            )
            return True
        
        except Exception as e:
            EmailLog.objects.create(
                recipient_email=seller.email,
                recipient_user=seller,
                email_type='LOW_STOCK_ALERT',
                subject=subject,
                status='FAILED',
                error_message=str(e)
            )
            return False
    
    @staticmethod
    def check_and_notify_low_stock(product):
        """check if a product is low stock and notify seller"""
        if product.stock_quantity <= 10 and product.is_active:
            return NotificationService.send_low_stock_alerts(product.seller)
        return False