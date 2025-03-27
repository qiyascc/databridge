from django.contrib import admin
from django.utils.html import format_html
from .models import ProductSitemap, ProductLocation, Product

@admin.register(ProductSitemap)
class ProductSitemapAdmin(admin.ModelAdmin):
    list_display = ('location', 'last_modification', 'update_date')
    search_fields = ('location',)

@admin.register(ProductLocation)
class ProductLocationAdmin(admin.ModelAdmin):
    list_display = ('location', 'lc_last_modification', 'priority', 'batch_id')
    list_filter = ('batch_id',)
    search_fields = ('location',)
from django.contrib import admin
from django.utils.html import format_html
from .models import ProductSitemap, ProductLocation, Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'title', 
        'category', 
        'color', 
        'price', 
        'discount_ratio', 
        'in_stock', 
        'available_sizes',
        'total_stock'
    )
    readonly_fields = ('total_stock', 'size_details')

    def available_sizes(self, obj):
        return ', '.join(obj.sizes.keys()) if obj.sizes else 'No sizes'
    available_sizes.short_description = 'Available Sizes'

    def total_stock(self, obj):
        return sum(size.get('general_stock', 0) for size in obj.sizes.values())
    total_stock.short_description = 'Total Stock'

    def size_details(self, obj):
        if not obj.sizes:
            return "No size information"
        
        html = "<table class='table'><tr><th>Size</th><th>Stock</th><th>Barcodes</th></tr>"
        for size, info in obj.sizes.items():
            html += f"""
            <tr>
                <td>{size}</td>
                <td>{info.get('general_stock', 0)}</td>
                <td>{', '.join(info.get('barcode_list', []))}</td>
            </tr>
            """
        html += "</table>"
        return format_html(html)
    size_details.short_description = 'Size Details'