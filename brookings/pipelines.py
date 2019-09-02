# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json

import pika
from scrapy.exceptions import DropItem

from brookings.items import SearchItem, ExpertItem, AbandonItem, ExpertContactItem
from brookings.models import Session, SearchSeed, ExpertsSeed, AbandonSeed, ExpertContactSeed


class BrookingsPipeline(object):
    def __init__(self, host, username, password, port, queue, switch):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.queue = queue
        self.switch = switch

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            host=crawler.settings.get("MQ_HOST"),
            username=crawler.settings.get("MQ_USERNAME"),
            password=crawler.settings.get("MQ_PASSWORD"),
            port=crawler.settings.get("MQ_PORT"),
            queue=crawler.settings.get("MQ_QUEUE"),
            switch=crawler.settings.get("MQ_SWITCH"),
        )

    def packaged_data(self, website, url, resource_urls, content="内容", resource_type=6):
        data = {
            "PlatFrom": website,
            "NewsUrl": url,
            "NewsContent": content,
            "ResourceType": resource_type,
            "ResourceUrl": resource_urls
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
            elif isinstance(item, AbandonItem):
                obj = AbandonSeed(**data)
                obj.save()
            elif isinstance(item, ExpertContactItem):
                obj = ExpertContactSeed(**data)
                obj.save()

            if self.switch:
                website = '布鲁金斯学会'
                url = data.get('url')
                pdf_file = data.get('pdf_file')
                resource_urls = json.loads(pdf_file).get("附件")
                if resource_urls:
                    body = self.packaged_data(website=website, url=url, resource_urls=resource_urls)
                    self.channel.basic_publish(exchange='', routing_key='zk_file_task_queue', body=body)
            return item
        except Exception as e:
            Session.rollback()
            raise DropItem(e)

    def open_spider(self, spider):
        self.credentials = pika.PlainCredentials(self.username, self.password)
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.host,
                                      port=self.port,
                                      credentials=self.credentials,
                                      heartbeat=0
                                      ))
        self.channel = self.connection.channel()
        # self.channel.queue_declare(queue=self.queue)

    def close_spider(self, spider):
        self.connection.close()
