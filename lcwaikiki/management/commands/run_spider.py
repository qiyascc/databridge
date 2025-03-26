from django.core.management.base import BaseCommand
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from databridge_scrapy.databridge_scrapy.spiders.lcwaikiki.get_product import LcGetProductsDataSpider
from databridge_scrapy.databridge_scrapy.spiders.lcwaikiki.get_product_location import ProductLocationSpider
from databridge_scrapy.databridge_scrapy.spiders.lcwaikiki.get_product_sitemap import LcwaikikiSitemapSpider

class Command(BaseCommand):
    help = 'Run Scrapy spiders as Django management commands'

    def add_arguments(self, parser):
        parser.add_argument(
            'spider',
            type=str,
            choices=['product', 'location', 'sitemap', 'all'],
            help='Which spider to run (product, location, sitemap, all)'
        )
        parser.add_argument(
            '--batch-id',
            type=int,
            default=0,
            help='Batch ID for product location spider'
        )

    def handle(self, *args, **options):
        process = CrawlerProcess(get_project_settings())
        spider_name = options['spider']
        
        if spider_name == 'product' or spider_name == 'all':
            process.crawl(LcGetProductsDataSpider)
        if spider_name == 'location' or spider_name == 'all':
            process.crawl(ProductLocationSpider, batch_id=options['batch_id'])
        if spider_name == 'sitemap' or spider_name == 'all':
            process.crawl(LcwaikikiSitemapSpider)
        
        process.start()