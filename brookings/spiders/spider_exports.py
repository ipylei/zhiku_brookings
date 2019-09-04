# -*- coding: utf-8 -*-
import json
import re

import scrapy

from brookings.config import parsing_rules
from brookings.items import ExpertItem, ExpertContactItem, AbandonItem


class ExpertsSpider(scrapy.Spider):
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

    @staticmethod
    def _get_experts_data(parsing_rule_dict, response):
        """解析专家页面
        :param category: 种类
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

        pdf_urls = response.xpath(parsing_rule_dict.get("pdf_file")).extract()
        pdf_file_dict = {'附件': pdf_urls}
        if pdf_file_dict.get('附件'):
            pdf_file = json.dumps(pdf_file_dict, ensure_ascii=False)
        else:
            pdf_file = None

        # 联系方式
        contact = dict()
        contact_selectors = response.xpath(parsing_rule_dict.get("contact"))
        for selector in contact_selectors:
            contact[selector.xpath("./@itemprop").extract_first()] = selector.xpath("./@href").extract_first()

        # 活跃的媒体
        active_media_dict = dict()
        active_media_selectors = response.xpath(parsing_rule_dict.get("active_media"))
        for media in active_media_selectors:
            active_media_dict[media.xpath("./@class").extract_first()] = media.xpath("./@href").extract_first()
        if active_media_dict:
            contact.update(active_media_dict)  # 更新联系方式，添加活跃的媒体
            active_media = json.dumps(active_media_dict, ensure_ascii=False)
        else:
            active_media = ''

        expert_grid_selectors = response.xpath(parsing_rule_dict.get("expert-grid"))
        try:
            topics_string = expert_grid_selectors.xpath('//dl').re_first(
                '<dt>[\s\S]*?Topics[\s\S]*?</dt>([\s\S]*?)<dt>')
            topics = ';'.join(re.findall('<dd><.*?>([\s\S]*?)<.*?></dd>', topics_string, re.S))
        except:
            topics = ''
        try:
            centers_string = expert_grid_selectors.xpath('//dl').re_first(
                '<dt>[\s\S]*?Centers[\s\S]*?</dt>([\s\S]*?)<dt>')
            centers = ';'.join(re.findall('<dd><.*?>([\s\S]*?)<.*?></dd>', centers_string, re.S))
        except:
            centers = ''
        try:
            projects_string = expert_grid_selectors.xpath('//dl').re_first(
                '<dt>[\s\S]*?Projects[\s\S]*?</dt>([\s\S]*?)<dt>')
            projects = ';'.join(
                re.findall('<dd><.*?>([\s\S]*?)<.*?></dd>', projects_string, re.S)) if projects_string else ''
        except:
            projects = ''
        try:
            addition_areas_string = expert_grid_selectors.xpath('//dl').re_first(
                '<dt>[\s\S]*?Additional Expertise Areas[\s\S]*?</dt>([\s\S]*?)<dt>')
            addition_areas = ';'.join(
                re.findall('<dd>([\s\S]*?)</dd>', addition_areas_string, re.S)) if addition_areas_string else ''
        except:
            addition_areas = ''
        try:
            current_positions_string = expert_grid_selectors.xpath('//dl').re_first(
                '<dt>[\s\S]*?Current Positions[\s\S]*?</dt>([\s\S]*?)<dt>')
            current_positions = ';'.join(
                re.findall('<dd>([\s\S]*?)</dd>', current_positions_string, re.S)) if current_positions_string else ''
        except:
            current_positions = ''
        try:
            past_positions_string = expert_grid_selectors.xpath('//dl').re_first(
                '<dt>[\s\S]*?Past Positions[\s\S]*?</dt>([\s\S]*?)<dt>')
            past_positions = ';'.join(
                re.findall('<dd>([\s\S]*?)</dd>', past_positions_string, re.S)) if past_positions_string else ''
        except:
            past_positions = ''
        try:
            languages_string = expert_grid_selectors.xpath('//dl').re_first(
                '<dt>[\s\S]*?Language Fluency[\s\S]*?</dt>([\s\S]*?)<dt>')
            languages = ';'.join(re.findall('<dd>([\s\S]*?)</dd>', languages_string, re.S))
        except:
            languages = ''

        last_dt_content = response.xpath(
            "//div[@class='expert-grid']/dl/dt[last()]/following-sibling::dd/text()").extract()
        last_dt_content = ';'.join(last_dt_content)
        last_dt_field = response.xpath("//div[@class='expert-grid']/dl/dt[last()]/text()").extract_first()
        if last_dt_field:
            last_dt_field = last_dt_field.strip().replace('"', '')
        if last_dt_field == 'Contact':  # 联系方式不在此列
            last_dt_field = None
        elif last_dt_field == 'Topics':
            last_dt_field = "topics"
        elif last_dt_field == "Centers":
            last_dt_field = "centers"
        elif last_dt_field == 'Projects':
            last_dt_field = "projects"
        elif last_dt_field == 'Additional Expertise Areas':
            last_dt_field = "addition_areas"
        elif last_dt_field == 'Current Positions':
            last_dt_field = "current_positions"
        elif last_dt_field == 'Past Positions':
            last_dt_field = "past_positions"
        elif last_dt_field == 'Education':
            last_dt_field = "education"
        elif last_dt_field == 'Language Fluency':
            last_dt_field = "languages"
        else:  # 其他不知名的不在此列
            last_dt_field = None

        data = {
            "name": name,
            "head_portrait": head_portrait,
            "brief_introd": brief_introd,
            "job": job,
            "research_field": research_field,
            "education": education,
            "pdf_file": pdf_file,
            "topics": topics,
            "centers": centers,
            "projects": projects,
            "addition_areas": addition_areas,
            "current_positions": current_positions,
            "past_positions": past_positions,
            "languages": languages,
            "url": response.url,
            "active_media": active_media,
            "contact": contact,
        }
        if last_dt_field:
            last_dt_field_dict = {last_dt_field: last_dt_content}
            data.update(last_dt_field_dict)
        return data

    def parse_expert(self, response):
        self.logger.warning(response.url)
        external_url = response.headers.get("Location")
        if external_url:
            external_url = external_url.decode()
        category = re.search('.*?brookings.edu/(.*?)/\S+', response.url)
        if category:
            category = category.group(1)
            if category == "experts":
                parsing_rule_dict = parsing_rules.get(category)
                data = self._get_experts_data(parsing_rule_dict, response)
                contacts = data.pop("contact")
                item = ExpertItem(**data)
                for key, value in contacts.items():
                    contact_data = {"url": response.url, "name": data.get("name"), "type": key, "contact": value}
                    item2 = ExpertContactItem(**contact_data)
                    yield item2  # 联系方式
                yield item
            else:
                data = {"status_code": response.status, "internal_url": response.url, "external_url": external_url}
                item = AbandonItem(**data)
                yield item
        else:
            data = {"status_code": response.status, "internal_url": response.url, "external_url": external_url}
            item = AbandonItem(**data)
            yield item
