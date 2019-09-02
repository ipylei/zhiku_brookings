# -*- coding: utf-8 -*-
import json
import re

import scrapy
from scrapy.http import HtmlResponse

from brookings.config import parsing_rules
from brookings.items import ExpertItem, ExpertContactItem


class ExpertSpider(scrapy.Spider):
    name = 'expert_spider'
    allowed_domains = ['brookings.edu']
    start_urls = ['https://www.brookings.edu/experts/']

    def parse(self, response):
        """解析专家列表页"""
        # 提取详情url
        urls = response.xpath("//div[@class='list-content']//article//*[@class='name']/a/@href").extract()
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_expert)

        next_url = response.xpath("//a[@class='load-more']/@href").extract_first()
        if next_url:
            yield scrapy.Request(url=next_url)

    def _get_experts_data(self, category, parsing_rule_dict, response):
        """解析专家页面
        :param category: 种类
        :param parsing_rule_dict: 专家页对应的解析规则字典
        :param reponse: 该页面响应
        :return: 各字段构造成的字典
        """
        name = response.xpath(parsing_rule_dict.get("name")).extract_first()
        head_portrait = response.xpath(parsing_rule_dict.get("head_portrait")).extract_first()
        brief_introd = response.xpath(parsing_rule_dict.get("brief_introd")).extract_first()
        jobs = response.xpath(parsing_rule_dict.get("job")).extract()
        job = [job.replace('-', '') for job in jobs]
        job = ';'.join(job)
        research_field = response.xpath(parsing_rule_dict.get("research_field")).extract()
        research_field = ';'.join(research_field)
        education = response.xpath(parsing_rule_dict.get("education")).extract()
        education = ';'.join(education)
        contact = response.xpath(parsing_rule_dict.get("contact")).extract()
        contact = ';'.join(contact)
        contact = contact.replace('#;', '')
        contact = contact.replace('#', '')
        pdf_urls = response.xpath(parsing_rule_dict.get("pdf_file")).extract()
        pdf_file_dict = {'附件': []}
        for i in range(len(pdf_urls)):
            annex_dict = dict()
            annex_dict['附件{}'.format(i + 1)] = pdf_urls[i]
            pdf_file_dict['附件'].append(annex_dict)
        pdf_file = json.dumps(pdf_file_dict, ensure_ascii=False)
        expert_grid = response.xpath(parsing_rule_dict.get("expert-grid")).extract_first()
        expert_response = HtmlResponse(url=response.url, body=expert_grid, encoding='utf8')
        try:
            topics_string = expert_response.xpath('//dl').re_first('<dt>[\s\S]*?Topics[\s\S]*?</dt>([\s\S]*?)<dt>')
            topics = ';'.join(re.findall('<dd><.*?>([\s\S]*?)<.*?></dd>', topics_string, re.S))
        except:
            topics = ''
        try:
            centers_string = expert_response.xpath('//dl').re_first('<dt>[\s\S]*?Centers[\s\S]*?</dt>([\s\S]*?)<dt>')
            centers = ';'.join(re.findall('<dd><.*?>([\s\S]*?)<.*?></dd>', centers_string, re.S))
        except:
            centers = ''
        try:
            projects_string = expert_response.xpath('//dl').re_first('<dt>[\s\S]*?Projects[\s\S]*?</dt>([\s\S]*?)<dt>')
            projects = ';'.join(
                re.findall('<dd><.*?>([\s\S]*?)<.*?></dd>', projects_string, re.S)) if projects_string else ''
        except:
            projects = ''
        try:
            addition_areas_string = expert_response.xpath('//dl').re_first(
                '<dt>[\s\S]*?Additional Expertise Areas[\s\S]*?</dt>([\s\S]*?)<dt>')
            addition_areas = ';'.join(
                re.findall('<dd>([\s\S]*?)</dd>', addition_areas_string, re.S)) if addition_areas_string else ''
        except:
            addition_areas = ''
        try:
            current_positions_string = expert_response.xpath('//dl').re_first(
                '<dt>[\s\S]*?Current Positions[\s\S]*?</dt>([\s\S]*?)<dt>')
            current_positions = ';'.join(
                re.findall('<dd>([\s\S]*?)</dd>', current_positions_string, re.S)) if current_positions_string else ''
        except:
            current_positions = ''
        try:
            past_positions_string = expert_response.xpath('//dl').re_first(
                '<dt>[\s\S]*?Past Positions[\s\S]*?</dt>([\s\S]*?)<dt>')
            past_positions = ';'.join(
                re.findall('<dd>([\s\S]*?)</dd>', past_positions_string, re.S)) if past_positions_string else ''
        except:
            past_positions = ''
        try:
            languages_string = expert_response.xpath('//dl').re_first(
                '<dt>[\s\S]*?Language Fluency[\s\S]*?</dt>([\s\S]*?)<dt>')
            languages = ';'.join(re.findall('<dd>([\s\S]*?)</dd>', languages_string, re.S))
        except:
            languages = ''

        data = {
            "name": name,
            "head_portrait": head_portrait,
            "brief_introd": brief_introd,
            "job": job,
            "research_field": research_field,
            "education": education,
            "contact": contact,
            "pdf_file": pdf_file,
            "topics": topics,
            "centers": centers,
            "projects": projects,
            "addition_areas": addition_areas,
            "current_positions": current_positions,
            "past_positions": past_positions,
            "languages": languages,
            "category": category,
            "url": response.url,
        }
        return data

    def parse_expert(self, response):
        category = re.search('.*?brookings.edu/(.*?)/\S+', response.url)
        if category:
            category = category.group(1)
            if category == "experts":
                parsing_rule_dict = parsing_rules.get(category)
                data = self._get_experts_data(category, parsing_rule_dict, response)
                data2 = {"name": data.get("name"), "contact": data.pop("contact")}
                item = ExpertItem(**data)
                item2 = ExpertContactItem(**data2)
                yield item
                yield item2
