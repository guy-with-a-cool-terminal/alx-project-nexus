from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from store.models import Category, Product, ProductImage

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with initial test data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')
        
        # Create test users
        seller, created = User.objects.get_or_create(
            username='testseller',
            defaults={
                'email': 'seller@test.com',
                'role': 'SELLER',
                'store_name': 'Tech Galaxy',
                'is_email_verified': True
            }
        )
        if created:
            seller.set_password('testpass123')
            seller.save()
            self.stdout.write('✅ Created test seller')
        
        consumer, created = User.objects.get_or_create(
            username='testbuyer',
            defaults={
                'email': 'buyer@test.com', 
                'role': 'CONSUMER',
                'is_email_verified': True
            }
        )
        if created:
            consumer.set_password('testpass123')
            consumer.save()
            self.stdout.write('✅ Created test consumer')

        # Create categories
        electronics, _ = Category.objects.get_or_create(
            name='Electronics',
            defaults={'description': 'Gadgets and devices'}
        )
        
        phones, _ = Category.objects.get_or_create(
            name='Phones',
            parent_category=electronics,
            defaults={'description': 'Smartphones and accessories'}
        )
        
        books, _ = Category.objects.get_or_create(
            name='Books',
            defaults={'description': 'Educational and entertainment'}
        )
        
        self.stdout.write('✅ Created categories')

        # Create sample products
        product1, created = Product.objects.get_or_create(
            name='Wireless Bluetooth Headphones',
            defaults={
                'description': 'High-quality noise cancelling headphones',
                'price': 99.99,
                'sku': 'AUDIO-001',
                'category': electronics,
                'seller': seller,
                'stock_quantity': 50,
                'brand': 'AudioTech',
                'tags': 'audio, wireless, bluetooth'
            }
        )
        
        if created:
            ProductImage.objects.create(
                product=product1,
                image='https://example.com/headphones.jpg',
                alt_text='Wireless Bluetooth Headphones',
                is_primary=True
            )
            self.stdout.write('✅ Created sample product 1')

        product2, created = Product.objects.get_or_create(
            name='Python Programming Book',
            defaults={
                'description': 'Learn Python from beginner to advanced',
                'price': 39.99,
                'sku': 'BOOK-001', 
                'category': books,
                'seller': seller,
                'stock_quantity': 100,
                'brand': 'CodePress',
                'tags': 'programming, python, education'
            }
        )
        
        if created:
            ProductImage.objects.create(
                product=product2,
                image='https://example.com/python-book.jpg',
                alt_text='Python Programming Book',
                is_primary=True
            )
            self.stdout.write('✅ Created sample product 2')

        self.stdout.write(self.style.SUCCESS('🎉 Database seeding completed!'))