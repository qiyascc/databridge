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
    search_fields = ('title', 'category', 'color')
    list_filter = (
        'category', 
        'in_stock', 
        'color'
    )
    
    readonly_fields = ('total_stock', 'size_details')
    
    def available_sizes(self, obj):
        """
        Display available sizes in admin list view
        """
        sizes = obj.get_available_sizes()
        return ', '.join(sizes.keys()) if sizes else 'No sizes'
    available_sizes.short_description = 'Available Sizes'
    
    def total_stock(self, obj):
        """
        Calculate total stock across all sizes
        """
        return sum(
            size_info.get('general_stock', 0) 
            for size_info in obj.sizes.values()
        )
    total_stock.short_description = 'Total Stock'
    
    def size_details(self, obj):
        """
        Detailed HTML view of size information
        """
        if not obj.sizes:
            return "No size information"
        
        html = "<table class='table'>"
        html += "<tr><th>Size</th><th>ID</th><th>Stock</th><th>Barcodes</th></tr>"
        
        for size, info in obj.sizes.items():
            html += f"""
            <tr>
                <td>{size}</td>
                <td>{info.get('size_id', 'N/A')}</td>
                <td>{info.get('general_stock', 0)}</td>
                <td>{', '.join(info.get('barcode_list', []))}</td>
            </tr>
            """
        
        html += "</table>"
        return format_html(html)
    size_details.short_description = 'Size Details'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'url', 'category', 'color')
        }),
        ('Pricing', {
            'fields': ('price', 'discount_ratio', 'in_stock')
        }),
        ('Media', {
            'fields': ('images',)
        }),
        ('Size Management', {
            'fields': ('sizes', 'size_details')
        }),
        ('System', {
            'fields': ('timestamp', 'status')
        })
    )

    def save_model(self, request, obj, form, change):
        """
        Custom save method to ensure sizes are properly processed
        """
        # Validate and clean sizes before saving
        if not isinstance(obj.sizes, dict):
            obj.sizes = {}
        
        super().save_model(request, obj, form, change)