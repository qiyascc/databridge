from django.core.management.base import BaseCommand
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import os
import django
from databridge_scrapy.databridge_scrapy.spiders.lcwaikiki.get_product import LcGetProductsDataSpider
from databridge_scrapy.databridge_scrapy.spiders.lcwaikiki.get_product_location import ProductLocationSpider
from databridge_scrapy.databridge_scrapy.spiders.lcwaikiki.get_product_sitemap import LcwaikikiSitemapSpider

class Command(BaseCommand):
    help = 'Run Scrapy spiders'

    def add_arguments(self, parser):
        parser.add_argument(
            'spider',
            type=str,
            choices=['product', 'location', 'sitemap', 'all'],
            help='Which spider to run'
        )
        parser.add_argument(
            '--batch-id',
            type=int,
            default=0,
            help='Batch ID for location spider'
        )

    def handle(self, *args, **options):
    # Django environment setup
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'databridge.settings')
        django.setup()

        # Scrapy settings
        settings = get_project_settings()
        settings.setmodule('databridge_scrapy.databridge_scrapy.settings')
        
        process = CrawlerProcess(settings)
        
        spider_name = options['spider']
        
        if spider_name == 'product' or spider_name == 'all':
            process.crawl(LcGetProductsDataSpider)
        if spider_name == 'location' or spider_name == 'all':
            process.crawl(
                ProductLocationSpider, 
                batch_id=options['batch_id']  # Burası düzeltildi
            )
        if spider_name == 'sitemap' or spider_name == 'all':
            process.crawl(LcwaikikiSitemapSpider)
        
        process.start()

