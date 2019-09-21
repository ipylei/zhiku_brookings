# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import time

import pika
from scrapy.exceptions import DropItem
from scrapy.http import HtmlResponse

from brookings.items import SearchItem, ExpertItem, AbandonItem, ExpertContactItem
from brookings.models import Session, SearchSeed, ExpertsSeed, AbandonSeed, ExpertContactSeed

DataSource_Dict = {
    "论坛": 1, "forum": 1,
    "微博": 2, "weibo": 2,
    "微信公众号": 3, "weixin": 3,
    "QQ群消息": 4, "qqqunmsg": 4,
    "新闻": 5, "news": 5,
    "博客": 6, "blog": 6,
    "贴吧": 7, "tieba": 7,
    "twitter": 8,
    "facebook": 9,
    "电子报刊": 10,
    "app": 11,
    "微信群": 12,
    "WhatsApp": 13,
    "line": 14,
    "telegram": 15,
    "搜索引擎": 16,
    "研究": 17, "research": 17,
    "报告": 18,
    "暗网": 20,
}


class BrookingsPipeline(object):

    def __init__(self,
                 # host,
                 # username,
                 # password,
                 # port,
                 news_queue,
                 expert_queue,
                 file_queue,
                 image_queue,
                 expert_img_queue,
                 switch, website):
        # self.host = host
        # self.username = username
        # self.password = password
        # self.port = port

        self.news_queue = news_queue
        self.expert_queue = expert_queue
        self.file_queue = file_queue
        self.image_queue = image_queue
        self.expert_img_queue = expert_img_queue
        self.switch = switch
        self.website = website

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            # host=crawler.settings.get("MQ_HOST"),
            # username=crawler.settings.get("MQ_USERNAME"),
            # password=crawler.settings.get("MQ_PASSWORD"),
            # port=crawler.settings.get("MQ_PORT"),
            news_queue=crawler.settings.get("MQ_NEWS_QUEUE"),
            expert_queue=crawler.settings.get("MQ_EXPERT_QUEUE"),
            file_queue=crawler.settings.get("MQ_FILE_QUEUE"),
            image_queue=crawler.settings.get("MQ_IMAGE_QUEUE"),
            expert_img_queue=crawler.settings.get("MQ_EXPERT_IMG_QUEUE"),
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

    def packaged_search(self, item):
        data = {
            "DBAttributeValue": {
                "DataType": 0,
                "DBType_En": "Detail",
                "DBTypeName": "详情",
                "IsSyncReturn": False,
                "TempMqName": "",
                "DBKey": "311_YQ_News_Appledaily_HK",
                "ProcName": "Proc_App_InsertNews",
                "ProcParaName": "news",
                "ParaConfigName": "news",
                "OptName": "",
                "OptTime": "",
                "Platform": 1271
            },
            "ListNews": [{
                "Platform": 0,
                "DataSource": 17,
                "PEID": 0,
                "PNID": "",
                "PRCID": "",
                "MediaSource": "",
                "MediaSourceUrl": "",
                # ...
                "ClickCount": 0,
                "CommentCount": 0,
                "CreateTime": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),
                "ModifyTime": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),
                "ForwardNum": 0,
                "LanguageCode": "en",
                "site_name": "brookings.edu",
                "country": self.website,
                "base_class_type": 7

            }
            ],
            "ListComments": ""
        }
        data_source = item.pop("DataSource")
        # data_source = item.get("DataSource")
        # if data_source and data_source.lower() in DataSource_Dict:
        #     item["DataSource"] = DataSource_Dict.get(data_source.lower())
        # else:
        #     item["DataSource"] = 17
        data['ListNews'][0].update(item)
        return json.dumps(data, ensure_ascii=False)

    def packaged_expert(self, item):
        data = {
            "DBAttributeValue": {
                "DataType": 0,
                "DBType_En": "Detail",
                "DBTypeName": "详情",
                "IsSyncReturn": False,
                "TempMqName": "",
                "DBKey": "311_YQ_News_Appledaily_HK",
                "ProcName": "Proc_App_InsertNews",
                "ProcParaName": "news",
                "ParaConfigName": "news",
                "OptName": "",
                "OptTime": "",
                "Platform": 1271
            },
            "experts": [{
                "createTime": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),
                "site_name": self.website
            }],
            "ListComments": ""
        }
        data["experts"][0].update(item)
        return json.dumps(data, ensure_ascii=False)

    def push_to_mq(self, item):
        """推送到RabbitMQ
        :param item:
        """
        pdf_file = item.pop("pdf_file") if item.get('pdf_file') else None

        # 推搜索
        if isinstance(item, SearchItem):
            body = self.packaged_search(item)
            self.channel.basic_publish(exchange='', routing_key=self.news_queue, body=body)
        # 推专家
        elif isinstance(item, ExpertItem):
            body = self.packaged_expert(item)
            self.channel.basic_publish(exchange='', routing_key=self.expert_queue, body=body)

        # 推其他
        url = item.get("Url")
        # 1.推送搜索内容或者专家的附件到MQ
        # pdf_file = item.get("pdf_file")
        if pdf_file:
            pdf_file_list = json.loads(pdf_file).get("附件")
            body = self.packaged_data(website=self.website, url=url, resource_urls=pdf_file_list,
                                      resource_type="Pdf")
            self.channel.basic_publish(exchange='', routing_key=self.file_queue, body=body)

        # 2.推送内容中的图片
        content = item.get("Content")
        if content:
            response = HtmlResponse(url=url, body=content, encoding='utf8')
            img_list = response.xpath("//img/@src").extract()
            if img_list:
                image_list = [response.urljoin(img_url) for img_url in img_list]
                body = self.packaged_data(website=self.website, url=url, resource_urls=image_list,
                                          resource_type="Picture", content=content)
                self.channel.basic_publish(exchange='', routing_key=self.image_queue, body=body)

        # 3.推送专家头像(图片)
        head_portrait = item.get("img_url")
        if head_portrait:
            body = self.packaged_data(website=self.website, url=url, resource_urls=[head_portrait],
                                      resource_type="Picture")
            self.channel.basic_publish(exchange='', routing_key=self.expert_img_queue, body=body)

    def process_item(self, item, spider):
        # try:
        #     if isinstance(item, SearchItem):
        #         obj = SearchSeed(**item)
        #         obj.save()
        #     elif isinstance(item, ExpertItem):
        #         obj = ExpertsSeed(**item)
        #         obj.save()
        #     elif isinstance(item, ExpertContactItem):
        #         obj = ExpertContactSeed(**item)
        #         obj.save()
        #     elif isinstance(item, AbandonItem):
        #         obj = AbandonSeed(**item)
        #         obj.save()

        if self.switch:
            self.push_to_mq(item)
        return item

    # except Exception as e:
    #     Session.rollback()
    #     raise DropItem(e)

    def open_spider(self, spider):
        """连接MQ
        :param spider:
        :return:
        """

        self.host = spider.mq_host
        self.port = spider.mq_port
        self.username = spider.mq_username
        self.password = spider.mq_password

        if self.switch:
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host,
                                                                                port=self.port,
                                                                                credentials=pika.PlainCredentials(
                                                                                    self.username, self.password),
                                                                                heartbeat=0))
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue=self.news_queue, durable=True)  # 内容图片队列
            self.channel.queue_declare(queue=self.expert_queue, durable=True)  # 内容图片队列
            self.channel.queue_declare(queue=self.image_queue, durable=True)  # 内容图片队列
            self.channel.queue_declare(queue=self.file_queue, durable=True)  # 附件队列
            self.channel.queue_declare(queue=self.expert_img_queue, durable=True)  # 专家头像队列

    def close_spider(self, spider):
        """关闭MQ
        :param spider:
        :return:
        """
        if self.switch:
            self.connection.close()
