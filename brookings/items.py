# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SearchItem(scrapy.Item):
    Url = scrapy.Field()
    Title = scrapy.Field()
    Author = scrapy.Field()
    PublishTime = scrapy.Field()
    Keywords = scrapy.Field()  # 关键字
    Abstract = scrapy.Field()  # 描述
    Content = scrapy.Field()
    Category = scrapy.Field()
    topic = scrapy.Field()
    tags = scrapy.Field()
    site_name = scrapy.Field()

    pdf_file = scrapy.Field()

    # editor = scrapy.Field()  # 编辑者
    # top_img = scrapy.Field()  # 标题图片


class ExpertItem(scrapy.Item):
    name = scrapy.Field()
    experts_url = scrapy.Field()

    # 可有可无
    img_url = scrapy.Field()
    abstract = scrapy.Field()
    research_field = scrapy.Field()
    job = scrapy.Field()
    education = scrapy.Field()
    contact = scrapy.Field()
    reward = scrapy.Field()
    active_media = scrapy.Field()
    createTime = scrapy.Field()
    relevant = scrapy.Field()
    # pdf_file = scrapy.Field()


class ExpertContactItem(scrapy.Item):
    url = scrapy.Field()
    name = scrapy.Field()
    type = scrapy.Field()
    contact = scrapy.Field()


class AbandonItem(scrapy.Item):
    status_code = scrapy.Field()
    internal_url = scrapy.Field()
    external_url = scrapy.Field()
