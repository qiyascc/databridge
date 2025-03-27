import scrapy
import xml.etree.ElementTree as ET
from datetime import datetime
from scrapy_djangoitem import DjangoItem
from lcwaikiki.models import ProductSitemap

class ProductSitemapItem(DjangoItem):
    django_model = ProductSitemap

class LcwaikikiSitemapSpider(scrapy.Spider):
    name = 'lc_get_product_sitemap'
    
    custom_settings = {
        'ITEM_PIPELINES': {
            'lcwaikiki.pipelines.DjangoPipeline': 300,
        },
        'LOG_LEVEL': 'DEBUG'
    }
    
    start_urls = ['https://www.lcw.com/sitemap/api/FeedXml/TR/product_sitemap.xml']

    def parse(self, response):
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        root = ET.fromstring(response.body)
        
        for sitemap in root.findall('.//ns:sitemap', namespace):
            item = ProductSitemapItem()
            item['location'] = sitemap.find('ns:loc', namespace).text
            item['last_modification'] = sitemap.find('ns:lastmod', namespace).text
            yield item