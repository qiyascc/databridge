import scrapy
import json
import re
from urllib.parse import urlparse
from typing import Dict, Any, Optional
from itemadapter import ItemAdapter
from datetime import datetime

class LcGetProductsDataSpider(scrapy.Spider):
    name = 'lc_get_product'
    
    custom_settings = {
        'FEEDS': {
            'lc_products_data.jsonl': {
                'format': 'jsonlines',
                'overwrite': True,
            }
        },
        'CONCURRENT_REQUESTS': 4,
        'DOWNLOAD_DELAY': 1,
        'RETRY_TIMES': 3
    }

    DEFAULT_CITY_ID = "865"
    INVENTORY_API_URL = "https://www.lcw.com/tr-TR/TR/ajax/Model/GetStoreInventoryMultiple"

    start_urls = [
        'https://www.lcw.com/beli-lastikli-erkek-cocuk-pantolon-mavi-o-4379059',
        'https://www.lcw.com/kravat-ve-mendil-kahverengi-o-682249',
        'https://www.lcw.com/slim-fit-dik-yaka-kapusonlu-reflektorlu-erkek-sisme-mont-gri-o-1428165',
        'https://www.lcw.com/standart-kalip-erkek-esofman-alti-lacivert-o-1459109',
        'https://www.lcw.com/standart-kalip-roller-erkek-sort-lacivert-o-1584696',
        'https://www.lcw.com/standart-kalip-roller-erkek-sort-siyah-o-1480645',
    ]

    def parse(self, response):
        meta_tags = self.extract_meta_tags(response)
        
        json_data = self.extract_json_data(response)

        if json_data is None:
            self.logger.error(f"No JSON data found for {response.url}")
            return

        product_sizes = json_data.get('ProductSizes', [])
        
        product = {
            "url": response.url,
            "title": json_data.get('PageTitle', ''),
            "category": json_data.get('CategoryName', ''),
            "color": json_data.get('Color', ''),
            "price": {
                "price": json_data.get('ProductPrices', {}).get('Price', ''),
                "discount_ratio": json_data.get('ProductPrices', {}).get('DiscountRatio', 0)
            },
            "in_stock": json_data.get('IsInStock', False),
            "sizes": [],
            "images": [
                img_url for pic in json_data.get('Pictures', [])
                for img_size in ['ExtraMedium600', 'ExtraMedium800', 'MediumImage', 'SmallImage']
                if (img_url := pic.get(img_size))
            ],
            "timestamp": datetime.now().isoformat(),
            "status": "success",
            "pending_size_requests": 0  # Track how many size requests we're waiting for
        }
        
        # Count how many sizes need inventory checks
        sizes_with_stock = [size for size in product_sizes if size.get('Stock', 0) > 0]
        product['pending_size_requests'] = len(sizes_with_stock)
        
        # If no sizes need inventory checks, yield immediately
        if not sizes_with_stock:
            for size in product_sizes:
                product['sizes'].append({
                    "size_name": size.get('Size', {}).get('Value', ''),
                    "size_id": size.get('Size', {}).get('SizeId', ''),
                    "size_general_stock": size.get('Stock', 0),
                    "product_option_size_reference": size.get('UrunOptionSizeRef', 0),
                    "barcode_list": size.get('BarcodeList', [])
                })
            yield product
            return
        
        # Process each size and request inventory if needed
        for size in product_sizes:
            size_info = {
                "size_name": size.get('Size', {}).get('Value', ''),
                "size_id": size.get('Size', {}).get('SizeId', ''),
                "size_general_stock": size.get('Stock', 0),
                "product_option_size_reference": size.get('UrunOptionSizeRef', 0),
                "barcode_list": size.get('BarcodeList', [])
            }
            
            if size_info['size_general_stock'] > 0:
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
                        "urunOptionSizeRef": str(size_info['product_option_size_reference'])
                    }),
                    callback=self.parse_inventory,
                    meta={
                        'product': product,
                        'size_info': size_info,
                        'original_url': response.url,
                        'dont_merge_cookies': True
                    }
                )
            else:
                # If no stock, just add the size info without city data
                product['sizes'].append(size_info)
                self.logger.debug(f"Size {size_info['size_name']} has no stock, skipping inventory check")

    def parse_inventory(self, response):
        product = response.meta['product']
        size_info = response.meta['size_info']
        original_url = response.meta['original_url']
        
        try:
            inventory_data = json.loads(response.text)
        except json.JSONDecodeError:
            self.logger.error(f"Failed to parse inventory JSON for {original_url}")
            inventory_data = {"storeInventoryInfos": []}
        
        city_stock = {}
        total_city_stock = 0
        
        for store in inventory_data.get('storeInventoryInfos', []):
            city_id = str(store.get('StoreCityId'))
            city_name = store.get('StoreCityName')
            
            if city_id not in city_stock:
                city_stock[city_id] = {
                    "name": city_name,
                    "stock": 0,
                    "stores": []
                }
            
            store_info = {
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
            }
            
            city_stock[city_id]['stores'].append(store_info)
            city_stock[city_id]['stock'] += store.get('Quantity', 0)
            total_city_stock += store.get('Quantity', 0)
        
        # Add city stock info to the size
        size_info['size_city_stock'] = city_stock
        size_info['size_general_stock'] = total_city_stock  # Update with actual total from API
        
        # Add the size to the product
        product['sizes'].append(size_info)
        
        # Decrement our pending requests counter
        product['pending_size_requests'] -= 1
        
        # Check if we've processed all inventory requests
        if product['pending_size_requests'] == 0:
            # Sort sizes by name for consistent output
            product['sizes'].sort(key=lambda x: x.get('size_name', ''))
            self.logger.debug(f"Yielding product with inventory data: {product}")
            yield product

    def extract_meta_tags(self, response) -> Dict[str, str]:
        """Extract all meta tags"""
        meta_tags = {}
        for meta in response.xpath('//meta'):
            name = meta.xpath('@name').get()
            property_ = meta.xpath('@property').get()
            content = meta.xpath('@content').get()
            
            if name:
                meta_tags[f'meta_name_{name}'] = content
            if property_:
                meta_tags[f'meta_property_{property_}'] = content
        
        return meta_tags

    def extract_json_data(self, response) -> Optional[Dict[str, Any]]:
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