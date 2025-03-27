import scrapy
import json
import re
from datetime import datetime
from scrapy_djangoitem import DjangoItem
from lcwaikiki.models import Product, ProductSize
from asgiref.sync import sync_to_async

class ProductItem(DjangoItem):
    django_model = Product

class ProductSizeItem(DjangoItem):
    django_model = ProductSize

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
    INVENTORY_API_URL = "https://www.lcw.com/tr-TR/TR/ajax/Model/GetStoreInventoryMultiple"

    start_urls = [
        'https://www.lcw.com/beli-lastikli-erkek-cocuk-pantolon-mavi-o-4379059',
        # Diğer URL'ler...
    ]

    async def parse(self, response):
        json_data = self.extract_json_data(response)
        if not json_data:
            self.logger.error(f"No JSON data found for {response.url}")
            return

        # Fiyatı temizle ve dönüştür
        price_str = json_data.get('ProductPrices', {}).get('Price', '0 TL')
        price = self.clean_price(price_str)

        # Ana ürün bilgilerini oluştur
        product_item = ProductItem()
        product_item['url'] = response.url
        product_item['title'] = json_data.get('PageTitle', '')
        product_item['category'] = json_data.get('CategoryName', '')
        product_item['color'] = json_data.get('Color', '')
        product_item['price'] = price
        product_item['discount_ratio'] = float(json_data.get('ProductPrices', {}).get('DiscountRatio', 0))
        product_item['in_stock'] = json_data.get('IsInStock', False)
        product_item['images'] = [
            img_url for pic in json_data.get('Pictures', [])
            for img_size in ['ExtraMedium600', 'ExtraMedium800', 'MediumImage', 'SmallImage']
            if (img_url := pic.get(img_size))
        ]
        product_item['status'] = "success"

        # Ürün boyutlarını işle
        product_sizes = json_data.get('ProductSizes', [])
        sizes_with_stock = [size for size in product_sizes if size.get('Stock', 0) > 0]
        
        # Bekleyen istek sayısını request.meta'da sakla
        request_meta = {
            'pending_size_requests': len(sizes_with_stock),
            'product_item': product_item,
            'original_url': response.url
        }

        if not sizes_with_stock:
            # Stok yoksa direkt tüm boyutları ekle
            for size in product_sizes:
                size_item = self.create_size_item(size)
                product_item['sizes'] = product_item.get('sizes', []) + [size_item]
            
            yield product_item
            return
        
        # Stok bilgisi için istek yap
        for size in product_sizes:
            if size.get('Stock', 0) > 0:
                request_meta['size_info'] = {
                    "size_name": size.get('Size', {}).get('Value', ''),
                    "size_id": size.get('Size', {}).get('SizeId', ''),
                    "size_general_stock": size.get('Stock', 0),
                    "product_option_size_reference": size.get('UrunOptionSizeRef', 0),
                    "barcode_list": size.get('BarcodeList', [])
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
                    # callback=self.parse_inventory,
                    # meta=request_meta,
                    # dont_merge_cookies=True
                )
            else:
                # Stok yoksa boyutu direkt ekle
                size_item = self.create_size_item(size)
                product_item['sizes'] = product_item.get('sizes', []) + [size_item]

    def create_size_item(self, size_data):
        """Boyut verisinden ProductSizeItem oluşturur"""
        size_item = ProductSizeItem()
        size_item.update({
            "size_name": size_data.get('Size', {}).get('Value', ''),
            "size_id": size_data.get('Size', {}).get('SizeId', ''),
            "size_general_stock": size_data.get('Stock', 0),
            "product_option_size_reference": size_data.get('UrunOptionSizeRef', 0),
            "barcode_list": size_data.get('BarcodeList', [])
        })
        return size_item

    async def parse_inventory(self, response):
        product_item = response.meta['product_item']
        size_info = response.meta['size_info']
        
        try:
            inventory_data = json.loads(response.text)
        except json.JSONDecodeError:
            self.logger.error(f"Failed to parse inventory JSON for {response.meta['original_url']}")
            inventory_data = {"storeInventoryInfos": []}
        
        # Stok bilgilerini işle
        city_stock = {}
        total_city_stock = 0
        
        for store in inventory_data.get('storeInventoryInfos', []):
            city_id = str(store.get('StoreCityId'))
            if city_id not in city_stock:
                city_stock[city_id] = {
                    "name": store.get('StoreCityName'),
                    "stock": 0,
                    "stores": []
                }
            
            city_stock[city_id]['stores'].append({
                "store_code": store.get('StoreCode', ''),
                "store_name": store.get('StoreName', ''),
                "store_address": {
                    "location_with_words": store.get('Address', ''),
                    "location_with_coordinants": [
                        store.get('Lattitude', ''),
                        store.get('Longitude', '')
                    ]
                },
                "store_phone": store.get('StorePhone', ''),
                "store_county": store.get('StoreCountyName', ''),
                "stock": store.get('Quantity', 0)
            })
            city_stock[city_id]['stock'] += store.get('Quantity', 0)
            total_city_stock += store.get('Quantity', 0)
        
        # Boyut item'ını güncelle
        size_item = self.create_size_item(size_info)
        size_item['size_city_stock'] = city_stock
        size_item['size_general_stock'] = total_city_stock
        
        # Ürün item'ına boyutu ekle
        product_item['sizes'] = product_item.get('sizes', []) + [size_item]
        
        # Bekleyen istek sayısını güncelle
        response.meta['pending_size_requests'] -= 1
        
        # Tüm boyutlar işlendiyse kaydet
        if response.meta['pending_size_requests'] <= 0:
            yield product_item

    def clean_price(self, price_str):
        """Fiyat string'ini float'a çevirir"""
        if not price_str:
            return 0.0
        
        try:
            cleaned = (price_str.replace(' TL', '')
                          .replace('₺', '')
                          .replace('.', '')
                          .replace(',', '.'))
            return float(cleaned)
        except ValueError:
            self.logger.warning(f"Could not convert price: {price_str}")
            return 0.0

    def extract_json_data(self, response):
        """JSON verisini çıkarır"""
        script_tags = response.xpath('//script[contains(text(), "cartOperationViewModel")]/text()').getall()
        
        for script in script_tags:
            try:
                pattern = r'cartOperationViewModel\s*=\s*({.*?});'
                match = re.search(pattern, script, re.DOTALL)
                if match:
                    json_str = match.group(1).strip()
                    json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)
                    json_str = re.sub(r',\s*}', '}', json_str)
                    json_str = re.sub(r',\s*]', ']', json_str)
                    return json.loads(json_str)
            except Exception as e:
                self.logger.error(f"JSON parsing error in {response.url}: {str(e)}")
                continue
        
        self.logger.warning(f"No valid JSON data found in {response.url}")
        return None