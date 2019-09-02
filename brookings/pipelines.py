# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json

import pika
from scrapy.exceptions import DropItem

from brookings.items import SearchItem, ExpertItem, ExternalItem, ExpertContactItem
from brookings.models import Session, SearchSeed, ExpertsSeed, ExternalSeed, ExpertContactSeed


class BrookingsPipeline(object):
    def push_mq(self, website, url, pdf_file):
        data = {
            "PlatFrom": website,
            "NewsUrl": url,
            "NewsContent": "内容",
            "ResourceType": 6,
            "ResourceUrl": json.loads(pdf_file).get("附件")
        }
        return json.dumps(data)

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

            website = '布鲁金斯学会'
            url = data.get('url')
            pdf_file = data.get('pdf_file')
            body = self.push_mq(website=website, url=url, pdf_file=pdf_file)
            self.channel.basic_publish(exchange='', routing_key='zk_file_task_queue', body=body)

        except Exception as e:
            Session.rollback()
            raise DropItem(e)

    def open_spider(self, spider):
        credentials = pika.PlainCredentials('guest', 'guest')
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='10.4.7.44', port=5672, credentials=credentials))
        self.channel = self.connection.channel()

    def close_spider(self, spider):
        self.connection.close()
