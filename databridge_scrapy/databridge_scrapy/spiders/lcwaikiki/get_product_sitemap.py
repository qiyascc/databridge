import scrapy
import xml.etree.ElementTree as ET
from datetime import datetime

class LcwaikikiSitemapSpider(scrapy.Spider):
    name = 'lc_get_product_sitemap'
    
    start_urls = ['https://www.lcw.com/sitemap/api/FeedXml/TR/product_sitemap.xml']

    def start_requests(self):
        for url in self.start_urls:
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Referer': 'https://www.lcw.com/',
            }

            yield scrapy.Request(url, self.parse, headers=headers)

    def parse(self, response):
        current_timestamp = datetime.now().isoformat()

        root = ET.fromstring(response.body)

        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

        for sitemap in root.findall('.//ns:sitemap', namespace):
            location = sitemap.find('ns:loc', namespace).text
            last_modified = sitemap.find('ns:lastmod', namespace).text

            yield {
                'location': location,
                'last_modification': last_modified,
                'update_date': current_timestamp
            }
