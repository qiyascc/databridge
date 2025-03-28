from asgiref.sync import sync_to_async
from scrapy.exceptions import DropItem
from django.db.utils import IntegrityError
from scrapy_djangoitem import DjangoItem
import logging

logger = logging.getLogger(__name__)

class DjangoPipeline:
    async def process_item(self, item, spider):
        try:
            if isinstance(item, DjangoItem):  # Sadece DjangoItem'ları işle
                await self._save_item(item)
            return item
        except Exception as e:
            spider.logger.error(f"❌ Kayıt hatası: {str(e)}")
            raise DropItem(f"Database error: {str(e)}")

    @sync_to_async
    def _save_item(self, item):
        model_class = item.django_model
        if not model_class.objects.filter(location=item['location']).exists():
            item.save()
            logger.info(f"✅ Veritabanına eklendi: {item['location']}")
        else:
            logger.info(f"⏩ Zaten var: {item['location']}")

from asgiref.sync import sync_to_async
from scrapy.exceptions import DropItem
import logging

logger = logging.getLogger(__name__)
from asgiref.sync import sync_to_async
from scrapy.exceptions import DropItem
import logging
# lcwaikiki/pipelines.py
from asgiref.sync import sync_to_async
from scrapy.exceptions import DropItem
from django.db import transaction
import logging
from .models import Product
class AsyncProductPipeline:
    async def process_item(self, item, spider):
        spider.logger.debug(f"Processing item: {dict(item)}")
        
        try:
            product, created = await self._save_product(item)
            if created:
                spider.logger.info(f"✅ Yeni ürün kaydedildi: {item.get('url')}")
            else:
                spider.logger.info(f"🔄 Ürün güncellendi: {item.get('url')}")
            return item
        except IntegrityError as e:
            spider.logger.error(f"❌ Veritabanı çakışması: {str(e)}")
            raise DropItem(f"Integrity error: {str(e)}")
        except Exception as e:
            spider.logger.error(f"❌ Beklenmeyen hata: {str(e)}", exc_info=True)
            raise DropItem(f"Unexpected error: {str(e)}")

    @sync_to_async
    def _save_product(self, item):
        from django.db import transaction
        from lcwaikiki.models import Product
        
        item_dict = dict(item)
        item_dict = {k: v for k, v in item_dict.items() if v is not None}
        
        with transaction.atomic():
            return Product.objects.update_or_create(
                url=item_dict['url'],
                defaults=item_dict
            )