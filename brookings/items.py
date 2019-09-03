# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SearchItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    publish_time = scrapy.Field()
    content = scrapy.Field()
    keywords = scrapy.Field()  # 关键字
    description = scrapy.Field()  # 描述
    editor = scrapy.Field()  # 编辑者
    author = scrapy.Field()
    topic = scrapy.Field()
    top_img = scrapy.Field()  # 标题图片
    tag = scrapy.Field()
    pdf_file = scrapy.Field()

    category = scrapy.Field()


class ExpertItem(scrapy.Item):
    name = scrapy.Field()
    head_portrait = scrapy.Field()  # 头像
    research_field = scrapy.Field()  # 研究领域
    brief_introd = scrapy.Field()  # 简介
    job = scrapy.Field()  # 职务
    education = scrapy.Field()  # 学历
    # contact = scrapy.Field()  # 联系方式
    reward = scrapy.Field()  # 获奖
    active_media = scrapy.Field()  # 活跃的媒体
    relevant = scrapy.Field()  # 相关计划

    url = scrapy.Field()
    pdf_file = scrapy.Field()  # 附件地址
    category = scrapy.Field()  # 栏目

    topics = scrapy.Field()
    centers = scrapy.Field()
    projects = scrapy.Field()
    addition_areas = scrapy.Field()
    current_positions = scrapy.Field()
    past_positions = scrapy.Field()
    languages = scrapy.Field()
    research_team = scrapy.Field()


class ExpertContactItem(scrapy.Item):
    name = scrapy.Field()
    contact = scrapy.Field()


class AbandonItem(scrapy.Item):
    status_code = scrapy.Field()
    internal_url = scrapy.Field()
    external_url = scrapy.Field()
