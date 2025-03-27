from django.db import models

class ProductSitemap(models.Model):
    location = models.URLField(max_length=500)
    last_modification = models.DateTimeField(null=True, blank=True)
    update_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Product Sitemap"
        verbose_name_plural = "Product Sitemaps"

class ProductLocation(models.Model):
    location = models.URLField(max_length=500)
    lc_last_modification = models.DateTimeField(null=True, blank=True)
    change_frequence = models.CharField(max_length=20, null=True, blank=True)
    priority = models.FloatField(null=True, blank=True)
    system_last_modification = models.DateTimeField(auto_now=True)
    batch_id = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = "Product Location"
        verbose_name_plural = "Product Locations"

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Product(models.Model):
    # Basic Product Information
    url = models.URLField(max_length=500, unique=True)
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    color = models.CharField(max_length=50)
    
    # Pricing and Availability
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_ratio = models.FloatField(
        default=0, 
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ]
    )
    in_stock = models.BooleanField(default=False)
    
    # Images
    images = models.JSONField(default=list)
    
    # Timestamp and Status
    timestamp = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=20, 
        default='success',
        choices=[
            ('success', 'Success'),
            ('pending', 'Pending'),
            ('error', 'Error')
        ]
    )
    
    # Advanced Size Management
    sizes = models.JSONField(default=dict, help_text="Structured size information")
    
    def add_size(self, size_name, size_id, general_stock, option_reference, barcodes=None, city_stocks=None):
        """
        Method to add or update size information
        """
        if not hasattr(self, '_sizes'):
            self._sizes = self.sizes or {}
        
        size_info = {
            'size_name': size_name,
            'size_id': size_id,
            'general_stock': general_stock,
            'product_option_size_reference': option_reference,
            'barcode_list': barcodes or [],
            'city_stock': city_stocks or {}
        }
        
        self._sizes[size_name] = size_info
        self.sizes = self._sizes
    
    def get_size(self, size_name):
        """
        Retrieve size information
        """
        return self.sizes.get(size_name)
    
    def get_available_sizes(self):
        """
        Return sizes with stock
        """
        return {
            size: info for size, info in self.sizes.items() 
            if info.get('general_stock', 0) > 0
        }
    
    def update_size_stock(self, size_name, new_stock, city=None):
        """
        Update stock for a specific size
        """
        if size_name in self.sizes:
            self.sizes[size_name]['general_stock'] = new_stock
            
            if city and 'city_stock' in self.sizes[size_name]:
                self.sizes[size_name]['city_stock'][city] = new_stock
            
            self.save()
    
    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        indexes = [
            models.Index(fields=['category', 'color']),
            models.Index(fields=['price']),
        ]
    
    def __str__(self):
        return self.title