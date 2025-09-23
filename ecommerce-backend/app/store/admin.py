from django.contrib import admin
from .models import User, Category, Product, ProductImage, ProductSale, EmailLog

admin.site.register(User)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(ProductSale)
admin.site.register(EmailLog)
