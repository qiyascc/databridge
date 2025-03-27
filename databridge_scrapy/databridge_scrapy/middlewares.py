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
import logging

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


# databridge/middlewares.py

from scrapy import signals
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.exceptions import IgnoreRequest
from urllib.parse import urlparse
import random
import base64
import logging
from fake_useragent import UserAgent

class CustomRetryMiddleware(RetryMiddleware):
    def __init__(self, settings):
        super().__init__(settings)
        self.max_retry_times = settings.getint('RETRY_TIMES')
        self.retry_http_codes = settings.getlist('RETRY_HTTP_CODES')
        self.priority_adjust = settings.getint('RETRY_PRIORITY_ADJUST')

    def process_response(self, request, response, spider):
        if response.status in self.retry_http_codes:
            reason = f"Status code {response.status} received"
            spider.logger.warning(f"Retrying due to {response.status} status code")
            return self._retry(request, reason, spider) or response
        return response

    def _retry(self, request, reason, spider):
        retries = request.meta.get('retry_times', 0) + 1

        if retries <= self.max_retry_times:
            spider.logger.debug(f"Retrying {request.url} (attempt {retries}/{self.max_retry_times})")
            
            # Proxy ve diğer meta verileri temizle
            new_request = request.copy()
            new_request.meta['retry_times'] = retries
            new_request.dont_filter = True
            
            # Proxy bilgilerini sıfırla
            if 'proxy' in new_request.meta:
                del new_request.meta['proxy']
            if 'current_proxy' in new_request.meta:
                del new_request.meta['current_proxy']
                
            return new_request
        else:
            spider.logger.error(f"Gave up retrying {request.url} after {retries} attempts")
            raise IgnoreRequest

class ProxyMiddleware:
    def __init__(self, proxies=None):
        self.proxies = proxies or []
        self.failed_proxies = set()
        self.logger = logging.getLogger(__name__)

    @classmethod
    def from_crawler(cls, crawler):
        proxies = crawler.settings.getlist('PROXIES', [])
        middleware = cls(proxies)
        crawler.signals.connect(middleware.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(middleware.spider_closed, signal=signals.spider_closed)
        return middleware

    def spider_opened(self, spider):
        spider.logger.info(f"Available proxies: {len(self.proxies)}")

    def spider_closed(self, spider):
        if self.failed_proxies:
            spider.logger.warning(f"Failed proxies: {len(self.failed_proxies)}")
        else:
            spider.logger.info("All proxies worked successfully")

    def process_request(self, request, spider):
        if 'proxy' not in request.meta and not request.meta.get('dont_proxy', False):
            proxy = self.get_random_proxy()
            if proxy:
                self.set_proxy(request, proxy)
                spider.logger.debug(f"Using proxy: {proxy}")

    def get_random_proxy(self):
        active_proxies = [p for p in self.proxies if p not in self.failed_proxies]
        
        if not active_proxies and self.proxies:
            self.logger.warning("All proxies failed, recycling proxy list")
            self.failed_proxies.clear()
            active_proxies = self.proxies.copy()
            
        return random.choice(active_proxies) if active_proxies else None

    def set_proxy(self, request, proxy_url):
        if '@' in proxy_url:
            parsed = urlparse(f'//{proxy_url}')
            credentials = f"{parsed.username}:{parsed.password}"
            proxy = f"http://{parsed.hostname}:{parsed.port}"
            
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            request.headers['Proxy-Authorization'] = f'Basic {encoded_credentials}'
            request.meta['proxy'] = proxy
        else:
            request.meta['proxy'] = f'http://{proxy_url}'

        request.meta['current_proxy'] = proxy_url

    def process_response(self, request, response, spider):
        if response.status in [403, 407, 429]:
            proxy = request.meta.get('current_proxy')
            if proxy:
                self.failed_proxies.add(proxy)
                spider.logger.warning(f"Marked proxy as failed: {proxy}")
                
            # RetryMiddleware'in tetiklenmesi için response döndür
            return response
        
        return response

    def process_exception(self, request, exception, spider):
        proxy = request.meta.get('current_proxy')
        if proxy:
            self.failed_proxies.add(proxy)
            spider.logger.warning(f"Proxy connection failed: {proxy}")
        
        # Yeni proxy ile yeniden deneme
        new_request = request.copy()
        new_request.dont_filter = True
        if 'proxy' in new_request.meta:
            del new_request.meta['proxy']
        if 'current_proxy' in new_request.meta:
            del new_request.meta['current_proxy']
            
        return new_request

class CustomUserAgentMiddleware:
    def __init__(self):
        self.ua = UserAgent()
        
    def process_request(self, request, spider):
        request.headers['User-Agent'] = self.ua.random
        spider.logger.debug(f"Using User-Agent: {request.headers['User-Agent']}")

