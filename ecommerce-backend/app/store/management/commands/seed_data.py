from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from store.models import Category, Product
from decimal import Decimal

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with extensive test data for demo'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database with demo data...')
        
        # Create test users
        seller, created = User.objects.get_or_create(
            username='techseller',
            defaults={
                'email': 'tech@example.com',
                'role': 'SELLER',
                'store_name': 'Tech Galaxy',
                'is_email_verified': True
            }
        )
        if created:
            seller.set_password('testpass123')
            seller.save()
            self.stdout.write('✅ Created tech seller')

        seller2, created = User.objects.get_or_create(
            username='bookseller',
            defaults={
                'email': 'books@example.com',
                'role': 'SELLER', 
                'store_name': 'Book Haven',
                'is_email_verified': True
            }
        )
        if created:
            seller2.set_password('testpass123')
            seller2.save()
            self.stdout.write('✅ Created book seller')

        # Create categories hierarchy
        electronics, _ = Category.objects.get_or_create(
            name='Electronics',
            defaults={'description': 'Gadgets and electronic devices'}
        )
        
        phones, _ = Category.objects.get_or_create(
            name='Smartphones',
            parent_category=electronics,
            defaults={'description': 'Mobile phones and accessories'}
        )
        
        laptops, _ = Category.objects.get_or_create(
            name='Laptops', 
            parent_category=electronics,
            defaults={'description': 'Laptops and notebooks'}
        )
        
        books, _ = Category.objects.get_or_create(
            name='Books',
            defaults={'description': 'Educational and entertainment books'}
        )
        
        fiction, _ = Category.objects.get_or_create(
            name='Fiction',
            parent_category=books,
            defaults={'description': 'Fiction novels and stories'}
        )
        
        programming, _ = Category.objects.get_or_create(
            name='Programming',
            parent_category=books, 
            defaults={'description': 'Programming and technical books'}
        )
        
        clothing, _ = Category.objects.get_or_create(
            name='Clothing',
            defaults={'description': 'Fashion and apparel'}
        )
        
        self.stdout.write('✅ Created categories hierarchy')

        # Sample products data - 35+ products for pagination demo
        products_data = [
            # Electronics - Smartphones
            {'name': 'iPhone 15 Pro', 'price': 999.99, 'category': phones, 'seller': seller, 
             'stock': 25, 'brand': 'Apple', 'sku': 'PHN-APP-001', 'tags': 'smartphone, apple, ios'},
            {'name': 'Samsung Galaxy S24', 'price': 849.99, 'category': phones, 'seller': seller,
             'stock': 30, 'brand': 'Samsung', 'sku': 'PHN-SAM-001', 'tags': 'smartphone, android, samsung'},
            {'name': 'Google Pixel 8', 'price': 699.99, 'category': phones, 'seller': seller,
             'stock': 15, 'brand': 'Google', 'sku': 'PHN-GGL-001', 'tags': 'smartphone, android, google'},
            {'name': 'OnePlus 12', 'price': 799.99, 'category': phones, 'seller': seller,
             'stock': 20, 'brand': 'OnePlus', 'sku': 'PHN-OPL-001', 'tags': 'smartphone, android, oneplus'},
            {'name': 'Xiaomi Mi 14', 'price': 599.99, 'category': phones, 'seller': seller,
             'stock': 40, 'brand': 'Xiaomi', 'sku': 'PHN-XMI-001', 'tags': 'smartphone, android, xiaomi'},
            
            # Electronics - Laptops
            {'name': 'MacBook Pro 16-inch', 'price': 2399.99, 'category': laptops, 'seller': seller,
             'stock': 10, 'brand': 'Apple', 'sku': 'LAP-APP-001', 'tags': 'laptop, apple, macos, professional'},
            {'name': 'Dell XPS 15', 'price': 1599.99, 'category': laptops, 'seller': seller,
             'stock': 18, 'brand': 'Dell', 'sku': 'LAP-DEL-001', 'tags': 'laptop, windows, dell, premium'},
            {'name': 'ThinkPad X1 Carbon', 'price': 1499.99, 'category': laptops, 'seller': seller,
             'stock': 12, 'brand': 'Lenovo', 'sku': 'LAP-LEN-001', 'tags': 'laptop, windows, lenovo, business'},
            {'name': 'ASUS ROG Zephyrus', 'price': 1899.99, 'category': laptops, 'seller': seller,
             'stock': 8, 'brand': 'ASUS', 'sku': 'LAP-ASU-001', 'tags': 'laptop, gaming, asus, windows'},
            {'name': 'HP Spectre x360', 'price': 1299.99, 'category': laptops, 'seller': seller,
             'stock': 22, 'brand': 'HP', 'sku': 'LAP-HP-001', 'tags': 'laptop, convertible, hp, windows'},
            
            # Programming Books
            {'name': 'Python Crash Course', 'price': 39.99, 'category': programming, 'seller': seller2,
             'stock': 50, 'brand': 'No Starch Press', 'sku': 'BK-PYT-001', 'tags': 'python, programming, beginner'},
            {'name': 'Clean Code: A Handbook', 'price': 49.99, 'category': programming, 'seller': seller2,
             'stock': 35, 'brand': 'Prentice Hall', 'sku': 'BK-CLC-001', 'tags': 'programming, best practices, clean code'},
            {'name': 'Design Patterns: Elements of Reusable Object-Oriented Software', 'price': 54.99, 'category': programming, 'seller': seller2,
             'stock': 28, 'brand': 'Addison-Wesley', 'sku': 'BK-DPT-001', 'tags': 'design patterns, oop, programming'},
            {'name': 'The Pragmatic Programmer', 'price': 44.99, 'category': programming, 'seller': seller2,
             'stock': 42, 'brand': 'Addison-Wesley', 'sku': 'BK-PGP-001', 'tags': 'programming, career, development'},
            {'name': 'JavaScript: The Good Parts', 'price': 29.99, 'category': programming, 'seller': seller2,
             'stock': 60, 'brand': "O'Reilly", 'sku': 'BK-JS-001', 'tags': 'javascript, web development, programming'},
            
            # Fiction Books
            {'name': 'The Great Gatsby', 'price': 12.99, 'category': fiction, 'seller': seller2,
             'stock': 100, 'brand': 'Scribner', 'sku': 'BK-FIC-001', 'tags': 'fiction, classic, literature'},
            {'name': 'To Kill a Mockingbird', 'price': 14.99, 'category': fiction, 'seller': seller2,
             'stock': 85, 'brand': 'HarperCollins', 'sku': 'BK-FIC-002', 'tags': 'fiction, classic, literature'},
            {'name': '1984', 'price': 13.99, 'category': fiction, 'seller': seller2,
             'stock': 75, 'brand': 'Secker & Warburg', 'sku': 'BK-FIC-003', 'tags': 'fiction, dystopian, classic'},
            {'name': 'Pride and Prejudice', 'price': 11.99, 'category': fiction, 'seller': seller2,
             'stock': 90, 'brand': 'Penguin Classics', 'sku': 'BK-FIC-004', 'tags': 'fiction, romance, classic'},
            {'name': 'The Hobbit', 'price': 16.99, 'category': fiction, 'seller': seller2,
             'stock': 65, 'brand': 'George Allen & Unwin', 'sku': 'BK-FIC-005', 'tags': 'fiction, fantasy, tolkien'},
            
            # More products for pagination
            {'name': 'Wireless Earbuds Pro', 'price': 129.99, 'category': electronics, 'seller': seller,
             'stock': 45, 'brand': 'Sony', 'sku': 'ELEC-SNY-001', 'tags': 'earbuds, wireless, audio, sony'},
            {'name': 'Smart Watch Series 8', 'price': 299.99, 'category': electronics, 'seller': seller,
             'stock': 30, 'brand': 'Apple', 'sku': 'ELEC-APP-002', 'tags': 'smartwatch, fitness, apple'},
            {'name': '4K Ultra HD TV 55-inch', 'price': 499.99, 'category': electronics, 'seller': seller,
             'stock': 15, 'brand': 'Samsung', 'sku': 'ELEC-SAM-002', 'tags': 'tv, 4k, samsung, entertainment'},
            {'name': 'Gaming Mechanical Keyboard', 'price': 89.99, 'category': electronics, 'seller': seller,
             'stock': 60, 'brand': 'Razer', 'sku': 'ELEC-RZR-001', 'tags': 'keyboard, gaming, mechanical, razer'},
            {'name': 'Wireless Gaming Mouse', 'price': 79.99, 'category': electronics, 'seller': seller,
             'stock': 55, 'brand': 'Logitech', 'sku': 'ELEC-LGT-001', 'tags': 'mouse, gaming, wireless, logitech'},
            
            # Low stock items for demo
            {'name': 'Limited Edition Novel', 'price': 24.99, 'category': fiction, 'seller': seller2,
             'stock': 3, 'brand': 'Special Editions', 'sku': 'BK-FIC-006', 'tags': 'fiction, limited, collector'},
            {'name': 'Vintage Typewriter', 'price': 199.99, 'category': electronics, 'seller': seller,
             'stock': 2, 'brand': 'Vintage', 'sku': 'ELEC-VIN-001', 'tags': 'vintage, typewriter, collector'},
            {'name': 'Out of Stock Test Item', 'price': 9.99, 'category': programming, 'seller': seller2,
             'stock': 0, 'brand': 'Test', 'sku': 'BK-TST-001', 'tags': 'test, programming, out of stock'},
            
            # More variety
            {'name': 'Python Data Science Handbook', 'price': 42.99, 'category': programming, 'seller': seller2,
             'stock': 38, 'brand': "O'Reilly", 'sku': 'BK-PYT-002', 'tags': 'python, data science, programming'},
            {'name': 'React Native Cookbook', 'price': 37.99, 'category': programming, 'seller': seller2,
             'stock': 25, 'brand': 'Packt', 'sku': 'BK-RCT-001', 'tags': 'react, mobile, programming'},
            {'name': 'System Design Interview', 'price': 34.99, 'category': programming, 'seller': seller2,
             'stock': 48, 'brand': 'ByteByteGo', 'sku': 'BK-SDI-001', 'tags': 'system design, interview, programming'},
            {'name': 'The Lord of the Rings Trilogy', 'price': 39.99, 'category': fiction, 'seller': seller2,
             'stock': 40, 'brand': 'HarperCollins', 'sku': 'BK-FIC-007', 'tags': 'fiction, fantasy, tolkien'},
            {'name': 'Harry Potter Complete Collection', 'price': 89.99, 'category': fiction, 'seller': seller2,
             'stock': 28, 'brand': 'Bloomsbury', 'sku': 'BK-FIC-008', 'tags': 'fiction, fantasy, harry potter'},
            {'name': 'Noise Cancelling Headphones', 'price': 199.99, 'category': electronics, 'seller': seller,
             'stock': 35, 'brand': 'Bose', 'sku': 'ELEC-BOS-001', 'tags': 'headphones, audio, bose, noise cancelling'},
            {'name': 'Bluetooth Speaker', 'price': 79.99, 'category': electronics, 'seller': seller,
             'stock': 50, 'brand': 'JBL', 'sku': 'ELEC-JBL-001', 'tags': 'speaker, bluetooth, audio, jbl'},
        ]

        created_count = 0
        for product_data in products_data:
            product, created = Product.objects.get_or_create(
                sku=product_data['sku'],
                defaults={
                    'name': product_data['name'],
                    'description': f"High-quality {product_data['name'].lower()} for your needs.",
                    'price': product_data['price'],
                    'category': product_data['category'],
                    'seller': product_data['seller'],
                    'stock_quantity': product_data['stock'],
                    'brand': product_data['brand'],
                    'tags': product_data['tags']
                }
            )
            if created:
                created_count += 1

        self.stdout.write(f'✅ Created {created_count} products')
        self.stdout.write(self.style.SUCCESS('🎉 Database seeding completed!'))
        self.stdout.write('📊 Demo ready: 35+ products, multiple categories, pagination visible')