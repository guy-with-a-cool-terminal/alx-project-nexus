from django.utils.text import slugify
from django.db import models

class Category(models.Model):
    # ... your existing fields ...
    
    def save(self, *args, **kwargs):
        """Auto-generate slug from name if empty, ensure uniqueness"""
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            
            # Ensure slug is unique
            while Category.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
                
            self.slug = slug
            
        super().save(*args, **kwargs)