# databridge/middlewares.py

import random
import base64
from urllib.parse import urlparse
from fake_useragent import UserAgent
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy import signals
from itemadapter import is_item, ItemAdapter
import logging

class ProxyMiddleware:
    def __init__(self, proxies=None):
        self.proxies = proxies or []
        self.failed_proxies = set()
        self.logger = logging.getLogger(__name__)

    @classmethod
    def from_crawler(cls, crawler):
        # Proxy listesini settings.py'den al
        proxies = crawler.settings.getlist('PROXIES', [])
        middleware = cls(proxies)
        crawler.signals.connect(middleware.spider_closed, signal=signals.spider_closed)
        return middleware

    def spider_closed(self, spider):
        # Spider kapandığında başarısız proxyleri logla
        if self.failed_proxies:
            spider.logger.warning(f"Failed proxies: {self.failed_proxies}")

    def get_random_proxy(self):
        # Çalışan proxy listesi oluştur (başarısız olanlar hariç)
        active_proxies = [p for p in self.proxies if p not in self.failed_proxies]
        
        if not active_proxies:
            # Tüm proxyler başarısız olduysa, hepsini tekrar dene
            self.failed_proxies.clear()
            active_proxies = self.proxies.copy()
            self.logger.warning("All proxies failed, resetting and trying again")
            
        return random.choice(active_proxies) if active_proxies else None

    def process_request(self, request, spider):
        # Özel bir proxy belirtilmemişse veya proxy kullanımı zorunluysa
        if 'proxy' not in request.meta and not request.meta.get('dont_proxy', False):
            proxy = self.get_random_proxy()
            if proxy:
                self.set_proxy(request, proxy)

    def set_proxy(self, request, proxy_url):
        # Proxy formatı 'username:password@host:port' olmalı
        if '@' in proxy_url:
            # Kimlikli proxy
            parsed = urlparse(f'//{proxy_url}')
            credentials = f"{parsed.username}:{parsed.password}"
            proxy = f"http://{parsed.hostname}:{parsed.port}"
            
            # Base64 encode credentials
            encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
            request.headers['Proxy-Authorization'] = f'Basic {encoded_credentials}'
            request.meta['proxy'] = proxy
        else:
            # Kimliksiz proxy
            request.meta['proxy'] = f'http://{proxy_url}'

        # Kullanılan proxy'yi logla
        request.meta['current_proxy'] = proxy_url

    def process_response(self, request, response, spider):
        # Proxy başarısız olmuşsa işaretle
        if response.status in [403, 407, 429, 500, 502, 503, 504]:
            proxy = request.meta.get('current_proxy')
            if proxy:
                self.failed_proxies.add(proxy)
                spider.logger.warning(f"Proxy failed and removed from pool: {proxy}")
        return response

    def process_exception(self, request, exception, spider):
        # Proxy bağlantı hatası olmuşsa işaretle
        proxy = request.meta.get('current_proxy')
        if proxy:
            self.failed_proxies.add(proxy)
            spider.logger.warning(f"Proxy connection error, removed from pool: {proxy}")
        
        # Yeni bir proxy seç ve isteği tekrar dene
        new_proxy = self.get_random_proxy()
        if new_proxy:
            self.set_proxy(request, new_proxy)
            return request