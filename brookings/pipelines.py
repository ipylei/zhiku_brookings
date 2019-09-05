# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json

import pika
from scrapy.exceptions import DropItem
from scrapy.http import HtmlResponse

from brookings.items import SearchItem, ExpertItem, AbandonItem, ExpertContactItem
from brookings.models import Session, SearchSeed, ExpertsSeed, AbandonSeed, ExpertContactSeed


class BrookingsPipeline(object):

    def __init__(self, host, username, password, port, file_queue, image_queue, expert_queue, switch, website):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.file_queue = file_queue
        self.image_queue = image_queue
        self.expert_queue = expert_queue
        self.switch = switch

        self.website = website

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            host=crawler.settings.get("MQ_HOST"),
            username=crawler.settings.get("MQ_USERNAME"),
            password=crawler.settings.get("MQ_PASSWORD"),
            port=crawler.settings.get("MQ_PORT"),
            file_queue=crawler.settings.get("MQ_FILE_QUEUE"),
            image_queue=crawler.settings.get("MQ_IMAGE_QUEUE"),
            expert_queue=crawler.settings.get("MQ_EXPERT_QUEUE"),
            switch=crawler.settings.get("MQ_SWITCH"),
            website=crawler.settings.get("WEBSITE")
        )

    @staticmethod
    def packaged_data(website, url, resource_urls, resource_type, content=""):
        """打包MQ要求的数据格式
        :param website:
        :param url:
        :param resource_urls:
        :param resource_type:
        :param content:
        :return:
        """
        data = {
            "PlatFrom": website,
            "newsContent": content,
            "newsUrl": url,
            "resourceType": resource_type,
            "resourceUrl": resource_urls
        }
        return json.dumps(data, ensure_ascii=False)

    def push_mq(self, item):
        """推送到RabbitMQ
        :param item:
        """
        url = item.get("url")

        # 1.推送搜索内容或者专家的附件到MQ
        pdf_file = item.get("pdf_file")
        if pdf_file:
            pdf_file_list = json.loads(pdf_file).get("附件")
            body = self.packaged_data(website=self.website, url=url, resource_urls=pdf_file_list,
                                      resource_type="Pdf")
            self.channel.basic_publish(exchange='', routing_key=self.file_queue, body=body)

        # 2.推送内容中的图片
        content = item.get("content")
        if content:
            response = HtmlResponse(url=url, body=content, encoding='utf8')
            img_list = response.xpath("//img/@src").extract()
            if img_list:
                image_list = [response.urljoin(img_url) for img_url in img_list]
                body = self.packaged_data(website=self.website, url=url, resource_urls=image_list,
                                          resource_type="Picture", content=content)
                self.channel.basic_publish(exchange='', routing_key=self.image_queue, body=body)

        # 3.推送专家头像(图片)
        head_portrait = item.get("head_portrait")
        if head_portrait:
            body = self.packaged_data(website=self.website, url=url, resource_urls=[head_portrait],
                                      resource_type="Picture")
            self.channel.basic_publish(exchange='', routing_key=self.expert_queue, body=body)

    def process_item(self, item, spider):
        try:
            if isinstance(item, SearchItem):
                obj = SearchSeed(**item)
                obj.save()
            elif isinstance(item, ExpertItem):
                obj = ExpertsSeed(**item)
                obj.save()
            elif isinstance(item, ExpertContactItem):
                obj = ExpertContactSeed(**item)
                obj.save()
            elif isinstance(item, AbandonItem):
                obj = AbandonSeed(**item)
                obj.save()

            if self.switch:
                self.push_mq(item)
            return item

        except Exception as e:
            Session.rollback()
            raise DropItem(e)

    def open_spider(self, spider):
        """连接MQ
        :param spider:
        :return:
        """
        if self.switch:
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host,
                                                                                port=self.port,
                                                                                credentials=pika.PlainCredentials(
                                                                                    self.username, self.password),
                                                                                heartbeat=0))
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue=self.image_queue, durable=True)  # 内容图片队列
            self.channel.queue_declare(queue=self.file_queue, durable=True)  # 附件队列
            self.channel.queue_declare(queue=self.expert_queue, durable=True)  # 专家头像队列

    def close_spider(self, spider):
        """关闭MQ
        :param spider:
        :return:
        """
        if self.switch:
            self.connection.close()
