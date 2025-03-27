# databridge_scrapy/databridge_scrapy/spiders/lcwaikiki/get_product.py
from urllib.error import HTTPError
import scrapy
import json
import re
from datetime import datetime
from scrapy.exceptions import CloseSpider
from scrapy_djangoitem import DjangoItem
from lcwaikiki.models import Product
from databridge_scrapy.databridge_scrapy.items import ProductItem

class LcGetProductsDataSpider(scrapy.Spider):
    name = 'lc_get_product'
    
    custom_settings = {
        'ITEM_PIPELINES': {
            'lcwaikiki.pipelines.AsyncProductPipeline': 300,
        },
        'CONCURRENT_REQUESTS': 4,
        'DOWNLOAD_DELAY': 1,
        'RETRY_TIMES': 3,
        'RETRY_HTTP_CODES': [403, 500, 502, 503, 504],
        'TWISTED_REACTOR': 'twisted.internet.asyncioreactor.AsyncioSelectorReactor',
        'DOWNLOADER_MIDDLEWARES': {
            'databridge_scrapy.databridge_scrapy.middlewares.ProxyMiddleware': 542,
            'databridge_scrapy.databridge_scrapy.middlewares.CustomRetryMiddleware': 541,
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
        }
    }

    DEFAULT_CITY_ID = "865"
    INVENTORY_API_URL = "https://www.lcw.com/tr/ajax/Model/GetStoreInventoryMultiple"
    MAX_RETRIES = 3
    start_urls = [
        'https://www.lcw.com/beli-lastikli-erkek-cocuk-pantolon-mavi-o-4379059',
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.failed_urls = []

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                callback=self.parse,
                errback=self.errback_handler,
                meta={
                    'original_url': url,
                    'retry_count': 0,
                    'handle_httpstatus_all': True
                }
            )

    async def parse(self, response):
        if response.status == 403:
            self.logger.warning(f"403 Forbidden received for {response.url}")
            new_request = self.retry_request(response)
            if new_request:
                yield new_request
            return

        json_data = self.extract_json_data(response)
        if not json_data:
            self.logger.error(f"No JSON data found for {response.url}")
            self.failed_urls.append(response.url)
            return

        try:
            product_data = self.prepare_product_data(response, json_data)
            product_sizes = json_data.get('ProductSizes', [])
            
            if not product_sizes:
                yield ProductItem(**product_data)
                return

            # Stoklu ürünleri işle
            # sizes_with_stock = [s for s in product_sizes if s.get('Stock', 0) > 0]
            sizes_with_stock = [s for s in product_sizes if isinstance(s, dict) and s.get('Stock', 0) > 0]
            meta = {
                'product_data': product_data,
                'original_url': response.url,
                'total_sizes': len(sizes_with_stock),
                'processed_sizes': []
            }

            for size in product_sizes:
                if not isinstance(size, dict):
                    continue
                if size.get('Stock', 0) > 0:
                    yield self.create_inventory_request(response, size, meta.copy())
                else:
                    self.add_size_to_product(product_data, size)

        except Exception as e:
            self.logger.error(f"Error processing product {response.url}: {str(e)}")
            yield self.retry_request(response, reason=f"parse_error:{str(e)}")

    def prepare_product_data(self, response, json_data):
        return {
            'url': response.url,
            'title': json_data.get('PageTitle', ''),
            'category': json_data.get('CategoryName', ''),
            'color': json_data.get('Color', ''),
            'price': self.clean_price(json_data.get('ProductPrices', {}).get('Price', '0 TL')),
            'discount_ratio': float(json_data.get('ProductPrices', {}).get('DiscountRatio', 0)),
            'in_stock': json_data.get('IsInStock', False),
            'images': self.extract_images(json_data),
            'status': "success",
            'sizes': {}
        }

    def process_product_sizes(self, response, product_data, json_data):
        product_sizes = json_data.get('ProductSizes', [])
        sizes_with_stock = [size for size in product_sizes if size.get('Stock', 0) > 0]
        
        if not sizes_with_stock:
            for size in product_sizes:
                self.add_size_to_product(product_data, size)
            yield ProductItem(**product_data)
            return

        meta = {
            'product_data': product_data,
            'original_url': response.meta['original_url'],
            'pending_requests': len(sizes_with_stock),
            'sizes_processed': 0
        }

        for size in product_sizes:
            if size.get('Stock', 0) > 0:
                yield self.create_inventory_request(response, size, meta)
            else:
                self.add_size_to_product(product_data, size)

    def create_inventory_request(self, response, size, meta):
        size_meta = meta.copy()
        size_meta.update({
            'current_size': {
                'name': size.get('Size', {}).get('Value', ''),
                'option_ref': size.get('UrunOptionSizeRef', 0)
            },
            'size_index': len(size_meta.get('processed_sizes', [])),
            'total_sizes': meta.get('total_sizes', 1),
            'processed_sizes': size_meta.get('processed_sizes', [])
        })
        
        return scrapy.Request(
            url=self.INVENTORY_API_URL,
            method='POST',
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                'Content-Type': 'application/json',
                'Referer': response.url,
                'X-Requested-With': 'XMLHttpRequest'
            },
            body=json.dumps({
                "cityId": self.DEFAULT_CITY_ID,
                "countyIds": [],
                "urunOptionSizeRef": str(size.get('UrunOptionSizeRef', 0))
            }),
            callback=self.parse_inventory,
            errback=self.errback_handler,
            meta=size_meta,
            # priority=10
        )

    async def parse_inventory(self, response):
        if response.status != 200:
            self.logger.warning(f"Invalid status {response.status} for inventory request")
            yield self.retry_request(response, reason=f"status_{response.status}")
            return

        try:
            product_data = response.meta['product_data']
            current_size = response.meta['current_size']
            inventory_data = json.loads(response.text)
            
            if not inventory_data.get('storeInventoryInfos'):
                self.logger.warning("Empty inventory data received")
                yield self.retry_request(response, reason="empty_inventory")
                return

            city_stock, total_stock = self.process_inventory_data(inventory_data)
            
            # Update product data with inventory info
            size_name = current_size['name']
            if size_name not in product_data['sizes']:
                product_data['sizes'][size_name] = {
                    'general_stock': 0,
                    'city_stock': {}
                }
                
            product_data['sizes'][size_name].update({
                'general_stock': total_stock,
                'city_stock': city_stock
            })
            
            # Track processed sizes
            processed_sizes = response.meta.get('processed_sizes', [])
            processed_sizes.append(size_name)
            response.meta['processed_sizes'] = processed_sizes
            
            # Check if all sizes processed
            if len(processed_sizes) >= response.meta.get('total_sizes', 1):
                yield ProductItem(**product_data)
                
        except json.JSONDecodeError:
            self.logger.error("Invalid JSON in inventory response")
            yield self.retry_request(response, reason="invalid_json")
        except Exception as e:
            self.logger.error(f"Inventory processing error: {str(e)}")
            yield self.retry_request(response, reason="processing_error")

    def process_inventory_data(self, inventory_data):
        city_stock = {}
        total_stock = 0
        
        for store in inventory_data.get('storeInventoryInfos', []):
            city_id = str(store.get('StoreCityId', ''))
            if city_id not in city_stock:
                city_stock[city_id] = {
                    'name': store.get('StoreCityName', ''),
                    'stock': 0,
                    'stores': []
                }
            
            store_info = {
                'store_code': store.get('StoreCode', ''),
                'store_name': store.get('StoreName', ''),
                'quantity': store.get('Quantity', 0),
                'location': {
                    'address': store.get('Address', ''),
                    'coordinates': [
                        store.get('Lattitude', ''),
                        store.get('Longitude', '')
                    ]
                }
            }
            
            city_stock[city_id]['stores'].append(store_info)
            city_stock[city_id]['stock'] += store_info['quantity']
            total_stock += store_info['quantity']
            
        return city_stock, total_stock

    def update_size_info(self, product_data, current_size, city_stock, total_stock):
        size_name = current_size['name']
        if size_name in product_data['sizes']:
            product_data['sizes'][size_name]['city_stock'] = city_stock
            product_data['sizes'][size_name]['general_stock'] = total_stock

    def retry_request(self, response):
        retries = response.meta.get('retry_count', 0)
        if retries < self.MAX_RETRIES:
            self.logger.info(f"Retrying {response.url} (attempt {retries + 1}/{self.MAX_RETRIES})")
            new_meta = response.meta.copy()
            new_meta['retry_count'] = retries + 1
            
            # Proxy ve User-Agent bilgilerini temizle
            if 'proxy' in new_meta:
                del new_meta['proxy']
            if 'current_proxy' in new_meta:
                del new_meta['current_proxy']
            if 'User-Agent' in response.request.headers:
                del response.request.headers['User-Agent']
            
            return response.request.replace(
                url=response.url,
                meta=new_meta,
                dont_filter=True
            )
        else:
            self.logger.error(f"Max retries reached for {response.url}")
            self.failed_urls.append(response.url)
            return None

    def errback_handler(self, failure):
        request = failure.request
        self.logger.error(f"Request failed: {request.url} - {repr(failure)}")
        
        if failure.check(HTTPError):
            response = failure.value.response
            if response.status == 403:
                return self.retry_request(response)
        return None

    # Diğer yardımcı metodlar (add_size_to_product, clean_price, extract_json_data) öncekiyle aynı kalacak

    def extract_images(self, json_data):
        """JSON verisinden resim URL'lerini çıkarır"""
        images = []
        for pic in json_data.get('Pictures', []):
            for size_type in ['ExtraMedium600', 'ExtraMedium800', 'MediumImage', 'SmallImage']:
                if img_url := pic.get(size_type):
                    images.append(img_url)
                    break  # Bir boyut bulunduğunda diğerlerini atla
        return images
    
    # ...
    def add_size_to_product(self, product_item, size_data):
        """Ürünün sizes alanına boyut ekler"""
        size_name = size_data.get('Size', {}).get('Value', '')
        product_item['sizes'][size_name] = {
            'size_id': size_data.get('Size', {}).get('SizeId', ''),
            'general_stock': size_data.get('Stock', 0),
            'product_option_size_reference': size_data.get('UrunOptionSizeRef', 0),
            'barcode_list': size_data.get('BarcodeList', []),
            'city_stock': {}
        }


    def clean_price(self, price_str):
        """Fiyat temizleme"""
        try:
            return float(
                price_str.replace(' TL', '')
                .replace('₺', '')
                .replace('.', '')
                .replace(',', '.')
            )
        except (ValueError, TypeError):
            self.logger.warning(f"Price conversion failed: {price_str}")
            return 0.0

    def extract_json_data(self, response):
        """Extract and validate JSON data from response"""
        try:
            script_content = response.xpath(
                '//script[contains(text(), "cartOperationViewModel")]/text()'
            ).get()
            
            if not script_content:
                self.logger.warning("No script content found containing cartOperationViewModel")
                return None
                
            match = re.search(
                r'cartOperationViewModel\s*=\s*({.*?});',
                script_content,
                re.DOTALL
            )
            
            if not match:
                self.logger.warning("Could not find JSON data in script content")
                return None
                
            json_str = match.group(1)
            json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)
            
            data = json.loads(json_str)
            if not isinstance(data, dict):
                raise ValueError("JSON data is not a dictionary")
                
            return data
            
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON decode error: {str(e)}")
        except Exception as e:
            self.logger.error(f"Error extracting JSON: {str(e)}")
            
        return None