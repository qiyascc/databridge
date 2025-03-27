import scrapy
from lxml import etree
from datetime import datetime
from scrapy_djangoitem import DjangoItem
from lcwaikiki.models import Product
from asgiref.sync import sync_to_async
from databridge_scrapy.databridge_scrapy.items import ProductLocationItem

class ProductLocationSpider(scrapy.Spider):
    name = 'lc_get_product_location'
    
    custom_settings = {
        'ITEM_PIPELINES': {
            'lcwaikiki.pipelines.DjangoPipeline': 300,
        },
        'CONCURRENT_REQUESTS': 4,
        'DOWNLOAD_DELAY': 1,
        'RETRY_TIMES': 3,
        'TWISTED_REACTOR': 'twisted.internet.asyncioreactor.AsyncioSelectorReactor'
    }

    start_urls = [
        'https://api.lcwaikiki.com/feed/service/api/TR/Products-1/xml',
        'https://api.lcwaikiki.com/feed/service/api/TR/Products-2/xml'
    ]

    def start_requests(self):
        for url in self.start_urls:
            headers = {
                'Accept': 'application/xml, text/xml, */*; q=0.01',
                'Accept-Language': 'en-US,en;q=0.5',
                'Referer': 'https://www.lcw.com/',
            }
            yield scrapy.Request(
                url, 
                self.parse, 
                headers=headers,
                meta={'batch_id': self.get_batch_id_from_url(url)}
            )

    def parse(self, response):
        current_timestamp = datetime.now().isoformat()
        batch_id = response.meta.get('batch_id', 0)
        
        try:
            xml_str = response.body.decode('utf-8')
            xml_str = xml_str.replace(' xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"', '')
            root = etree.fromstring(xml_str.encode('utf-8'))

            for url_elem in root.findall('.//url'):
                try:
                    item = ProductLocationItem()  # Dictionary yerine DjangoItem kullanın
                    item['location'] = url_elem.findtext('loc', '')
                    item['lc_last_modification'] = url_elem.findtext('lastmod', None)
                    item['change_frequence'] = url_elem.findtext('changefreq', None)
                    item['priority'] = float(url_elem.findtext('priority', 0)) if url_elem.findtext('priority') else None
                    item['system_last_modification'] = datetime.now()
                    item['batch_id'] = response.meta['batch_id']
                    
                    yield item
                        
                except Exception as e:
                    self.logger.error(f"Error processing individual URL: {str(e)}")
                    yield {
                        'error': str(e),
                        'batch_id': batch_id,
                        'timestamp': current_timestamp
                    }

        except Exception as e:
            self.logger.error(f"Error parsing XML: {str(e)}")
            yield {
                'error': f"XML parsing error: {str(e)}",
                'batch_id': batch_id,
                'timestamp': current_timestamp
            }

    def get_batch_id_from_url(self, url):
        try:
            return int(url.split('-')[-1].split('.')[0])
        except (IndexError, ValueError):
            return 0