# databridge_scrapy/databridge_scrapy/spiders/lcwaikiki/get_product.py
import scrapy
import json
import re
from datetime import datetime
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
        'TWISTED_REACTOR': 'twisted.internet.asyncioreactor.AsyncioSelectorReactor'
    }

    DEFAULT_CITY_ID = "865"
    INVENTORY_API_URL = "https://www.lcw.com/tr/ajax/Model/GetStoreInventoryMultiple/"

    start_urls = [
        'https://www.lcw.com/beli-lastikli-erkek-cocuk-pantolon-mavi-o-4379059',
    ]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                callback=self.parse,
                meta={'original_url': url}
            )

    async def parse(self, response):
        json_data = self.extract_json_data(response)
        if not json_data:
            self.logger.error(f"No JSON data found for {response.url}")
            return

        # Ana ürün verilerini topla
        product_data = {
            'url': response.url,
            'title': json_data.get('PageTitle', ''),
            'category': json_data.get('CategoryName', ''),
            'color': json_data.get('Color', ''),
            'price': self.clean_price(json_data.get('ProductPrices', {}).get('Price', '0 TL')),
            'discount_ratio': float(json_data.get('ProductPrices', {}).get('DiscountRatio', 0)),
            'in_stock': json_data.get('IsInStock', False),
            'images': [
                img_url for pic in json_data.get('Pictures', [])
                for img_size in ['ExtraMedium600', 'ExtraMedium800', 'MediumImage', 'SmallImage']
                if (img_url := pic.get(img_size))
            ],
            'status': "success",
            'sizes': {}
        }

        product_sizes = json_data.get('ProductSizes', [])
        sizes_with_stock = [size for size in product_sizes if size.get('Stock', 0) > 0]
        
        # Meta veriyi hazırla
        meta = {
            'product_data': product_data,
            'original_url': response.meta['original_url'],
            'pending_requests': len(sizes_with_stock),
            'sizes_processed': 0
        }

        if not sizes_with_stock:
            # Stok yoksa direkt kaydet
            for size in product_sizes:
                self.add_size_to_product(product_data, size)
            yield ProductItem(**product_data)
            return

        # Stok bilgisi için istek yap
        for size in product_sizes:
            if size.get('Stock', 0) > 0:
                size_meta = meta.copy()
                size_meta['current_size'] = {
                    'name': size.get('Size', {}).get('Value', ''),
                    'option_ref': size.get('UrunOptionSizeRef', 0)
                }
                yield scrapy.Request(
                    url=self.INVENTORY_API_URL,
                    method='POST',
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                        'Content-Type': 'application/json',
                        'Referer': response.url
                    },
                    body=json.dumps({
                        "cityId": self.DEFAULT_CITY_ID,
                        "countyIds": [],
                        "urunOptionSizeRef": str(size.get('UrunOptionSizeRef', 0))
                    }),
                    callback=self.parse_inventory,
                    meta=size_meta
                )
            else:
                self.add_size_to_product(product_data, size)

    def add_size_to_product(self, product_data, size_data):
        """Ürün verisine boyut ekler"""
        size_name = size_data.get('Size', {}).get('Value', '')
        product_data['sizes'][size_name] = {
            'size_id': size_data.get('Size', {}).get('SizeId', ''),
            'general_stock': size_data.get('Stock', 0),
            'product_option_size_reference': size_data.get('UrunOptionSizeRef', 0),
            'barcode_list': size_data.get('BarcodeList', []),
            'city_stock': {}
        }

    async def parse_inventory(self, response):
        product_data = response.meta['product_data']
        current_size = response.meta['current_size']
        
        try:
            inventory_data = json.loads(response.text)
        except json.JSONDecodeError:
            self.logger.error(f"Invalid JSON response for {response.url}")
            inventory_data = {"storeInventoryInfos": []}

        # Şehir stok bilgilerini işle
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
            
            city_stock[city_id]['stores'].append({
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
            })
            city_stock[city_id]['stock'] += store.get('Quantity', 0)
            total_stock += store.get('Quantity', 0)

        # Boyut bilgisini güncelle
        size_name = current_size['name']
        if size_name in product_data['sizes']:
            product_data['sizes'][size_name]['city_stock'] = city_stock
            product_data['sizes'][size_name]['general_stock'] = total_stock

        # İlerlemeyi takip et
        response.meta['sizes_processed'] += 1
        
        # Tüm istekler tamamlandığında
        if response.meta['sizes_processed'] >= response.meta['pending_requests']:
            yield ProductItem(**product_data)

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
        """JSON verisi çıkarma"""
        try:
            script_content = response.xpath(
                '//script[contains(text(), "cartOperationViewModel")]/text()'
            ).get()
            
            json_str = re.search(
                r'cartOperationViewModel\s*=\s*({.*?});', 
                script_content, 
                re.DOTALL
            ).group(1)
            
            # JSON temizleme
            json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)
            return json.loads(json_str)
        except Exception as e:
            self.logger.error(f"JSON extraction failed: {str(e)}")
            return None

