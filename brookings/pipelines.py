# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


from scrapy.exceptions import DropItem

from brookings.items import SearchItem, ExpertItem
from brookings.models import Session, SearchSeed, ExpertsSeed


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
        except Exception as e:
            Session.rollback()
            raise DropItem(e)
