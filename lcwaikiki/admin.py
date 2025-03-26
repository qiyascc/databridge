from django.contrib import admin
from .models import ProductSitemap, ProductLocation, Product, ProductSize

@admin.register(ProductSitemap)
class ProductSitemapAdmin(admin.ModelAdmin):
    list_display = ('location', 'last_modification', 'update_date')
    search_fields = ('location',)

@admin.register(ProductLocation)
class ProductLocationAdmin(admin.ModelAdmin):
    list_display = ('location', 'lc_last_modification', 'priority', 'batch_id')
    list_filter = ('batch_id',)
    search_fields = ('location',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'color', 'price', 'discount_ratio', 'in_stock')
    search_fields = ('title', 'category', 'color')
    list_filter = ('category', 'in_stock')

@admin.register(ProductSize)
class ProductSizeAdmin(admin.ModelAdmin):
    list_display = ('product', 'size_name', 'size_general_stock')
    search_fields = ('product__title', 'size_name')
    list_filter = ('size_name',)