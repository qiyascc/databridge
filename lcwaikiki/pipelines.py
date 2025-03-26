from itemadapter import ItemAdapter
from scrapy_app.databridge.items import (
    ProductSitemapItem, 
    ProductLocationItem, 
    ProductItem,
    ProductSizeItem
)

class DjangoPipeline:
    def process_item(self, item, spider):
        if isinstance(item, (ProductSitemapItem, ProductLocationItem, ProductItem, ProductSizeItem)):
            item.save()
            spider.logger.info(f"Item saved to Django database: {item}")
        return item

