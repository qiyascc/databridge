from asgiref.sync import sync_to_async
from scrapy.exceptions import DropItem
from django.db.utils import IntegrityError
import logging

logger = logging.getLogger(__name__)

class DjangoPipeline:
    
    async def process_item(self, item, spider):
        try:
            await self._save_item(item, spider)
            return item
        except Exception as e:
            spider.logger.error(f"❌ Kayıt hatası: {str(e)}")
            raise DropItem(f"Database error: {str(e)}")

    @sync_to_async
    def _save_item(self, item, spider):
        if hasattr(item, 'save'):
            if not item.__class__.django_model.objects.filter(location=item['location']).exists():
                item.save()
                spider.logger.info(f"✅ Veritabanına eklendi: {item['location']}")
            else:
                spider.logger.info(f"⏩ Zaten var: {item['location']}")

from asgiref.sync import sync_to_async
from scrapy.exceptions import DropItem
import logging

logger = logging.getLogger(__name__)

class AsyncProductPipeline:
    
    async def process_item(self, item, spider):
        try:
            if isinstance(item, dict) and 'sizes' in item:  # Ana ürün için
                await self._save_product_with_sizes(item, spider)
            elif hasattr(item, 'django_model'):  # Tekil item'lar için
                await sync_to_async(item.save)()
            return item
        except Exception as e:
            spider.logger.error(f"❌ Kayıt hatası: {str(e)}")
            raise DropItem(f"Database error: {str(e)}")

    @sync_to_async
    def _save_product_with_sizes(self, product_data, spider):
        # Ana ürünü kaydet
        product_item = product_data['product_item']
        product = product_item.save(commit=False)
        product.save()
        
        # Boyutları kaydet
        for size_data in product_data.get('sizes', []):
            size_item = size_data['size_item']
            size = size_item.save(commit=False)
            size.product = product
            size.save()
        
        spider.logger.info(f"✅ Ürün ve {len(product_data['sizes'])} boyut kaydedildi")