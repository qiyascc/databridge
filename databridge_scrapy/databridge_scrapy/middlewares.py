# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from scrapy import settings
# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter
import random
import base64
from fake_useragent import UserAgent
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.core.downloader.handlers.http11 import HTTP11DownloadHandler
from urllib.parse import urlparse

class DatabridgeSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class DatabridgeDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)

# databridge/databridge/middlewares.py


class CustomUserAgentMiddleware:
    def __init__(self, user_agent=''):
        self.user_agent = user_agent or UserAgent().random

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings.get('USER_AGENT', ''))

    def process_request(self, request, spider):
        request.headers['User-Agent'] = self.user_agent

class ProxyMiddleware:
    def __init__(self, proxies=None):
        self.proxies = proxies or []
        self.current_proxy = None

    @classmethod
    def from_crawler(cls, crawler):
        # Proxy listesini settings.py'den alabilirsiniz
        proxies = crawler.settings.getlist('PROXIES', [])
        return cls(proxies)

    def process_request(self, request, spider):
        if self.proxies:
            # Aktif proxy yoksa veya tüm proxyleri denediyseniz yeni bir proxy seçin
            if not self.current_proxy or self.current_proxy not in self.proxies:
                self.current_proxy = random.choice(self.proxies)
            
            # Proxy formatı 'username:password@host:port' olmalı
            if '@' in self.current_proxy:
                # Kimlikli proxy
                parsed = urlparse(f'//{self.current_proxy}')
                credentials = f"{parsed.username}:{parsed.password}"
                proxy_url = f"http://{parsed.hostname}:{parsed.port}"
                
                # Base64 encode credentials
                encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
                request.headers['Proxy-Authorization'] = f'Basic {encoded_credentials}'
                request.meta['proxy'] = proxy_url
            else:
                # Kimliksiz proxy
                request.meta['proxy'] = f'http://{self.current_proxy}'

class CustomRetryMiddleware(RetryMiddleware):
    def __init__(self, settings):
        super().__init__(settings)
        # Özel retry davranışları eklenebilir
        self.max_retry_times = settings.getint('RETRY_TIMES', 3)
        self.retry_http_codes = settings.getlist('RETRY_HTTP_CODES', [500, 502, 503, 504, 522, 524, 408])

    def delete_failed_proxy(self, request):
        # Başarısız proxy'yi listeden çıkar
        proxy = request.meta.get('proxy', '')
        if proxy and hasattr(self, 'proxies'):
            self.proxies.remove(proxy)

