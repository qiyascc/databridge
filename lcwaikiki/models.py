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

class Product(models.Model):
    url = models.URLField(max_length=500, unique=True)
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    color = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_ratio = models.FloatField(default=0)
    in_stock = models.BooleanField(default=False)
    images = models.JSONField(default=list)
    timestamp = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, default='success')
    
    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"

class ProductSize(models.Model):
    product = models.ForeignKey(Product, related_name='sizes', on_delete=models.CASCADE)
    size_name = models.CharField(max_length=50)
    size_id = models.CharField(max_length=50)
    size_general_stock = models.IntegerField(default=0)
    product_option_size_reference = models.IntegerField()
    barcode_list = models.JSONField(default=list)
    size_city_stock = models.JSONField(default=dict)
    
    class Meta:
        verbose_name = "Product Size"
        verbose_name_plural = "Product Sizes"