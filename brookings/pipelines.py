# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


from scrapy.exceptions import DropItem

from brookings.items import SearchItem, ExpertItem, ExternalItem, ExpertContactItem
from brookings.models import Session, SearchSeed, ExpertsSeed, ExternalSeed, ExpertContactSeed


class BrookingsPipeline(object):
    def process_item(self, item, spider):
        data = dict(item)
        try:
            if isinstance(item, SearchItem):
                obj = SearchSeed(**data)
                obj.save()
            elif isinstance(item, ExpertItem):
                obj = ExpertsSeed(**data)
                obj.save()
            elif isinstance(item, ExternalItem):
                obj = ExternalSeed(**data)
                obj.save()
            elif isinstance(item, ExpertContactItem):
                obj = ExpertContactSeed(**data)
                obj.save()
        except Exception as e:
            Session.rollback()
            raise DropItem(e)
