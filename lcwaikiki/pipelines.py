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

logger = logging.getLogger(__name__)

class AsyncProductPipeline:
    async def process_item(self, item, spider):
        try:
            await self._save_product(item)
            return item
        except Exception as e:
            spider.logger.error(f"Database error: {str(e)}")
            raise DropItem(f"Failed to save item: {str(e)}")

    @sync_to_async
    def _save_product(self, item):
        with transaction.atomic():
            defaults = {
                'title': item.get('title'),
                'category': item.get('category'),
                'color': item.get('color'),
                'price': item.get('price'),
                'discount_ratio': item.get('discount_ratio'),
                'in_stock': item.get('in_stock'),
                'images': item.get('images'),
                'sizes': item.get('sizes'),
                'status': item.get('status')
            }
            
            product, created = Product.objects.update_or_create(
                url=item['url'],
                defaults=defaults
            )
            
            action = "Created" if created else "Updated"
            logger.info(f"{action} product: {product.url}")