from scrapy_djangoitem import DjangoItem
from lcwaikiki.models import ProductSitemap, ProductLocation, Product, ProductSize

class ProductSitemapItem(DjangoItem):
    django_model = ProductSitemap

class ProductLocationItem(DjangoItem):
    django_model = ProductLocation

class ProductItem(DjangoItem):
    django_model = Product

class ProductSizeItem(DjangoItem):
    django_model = ProductSize