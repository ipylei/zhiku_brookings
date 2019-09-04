# -*- coding: utf-8 -*-
import json
import re
import datetime

import scrapy
from scrapy.linkextractors import LinkExtractor

from brookings.settings import PAGE_COUNT
from brookings.config import parsing_rules
from brookings.items import SearchItem, ExpertItem, AbandonItem, ExpertContactItem


class SearchSpider(scrapy.Spider):
    name = 'search_spider'
    # allowed_domains = ['brookings.edu']
    page_count = 0
    basic_url = 'https://www.brookings.edu/search/?s={}'
    item_xpath_list = [
        "//div[@class='list-content']/article//a[@class='event-content']",  # events
        "//div[@class='list-content']/article//h4[@class='title']/a", ]

    def start_requests(self):
        search_words = 'events'
        start_url = self.basic_url.format(search_words)
        # start_url = "https://www.brookings.edu/search/?s=&post_type=essay&topic=&pcp=&date_range=&start_date=&end_date="
        yield scrapy.Request(url=start_url)

    def parse(self, response):
        """解析列表页
        :param response:
        :return:
        """
        self.page_count += 1
        if self.page_count <= PAGE_COUNT:
            # 提取详情url
            item_le = LinkExtractor(restrict_xpaths=self.item_xpath_list)
            item_links = item_le.extract_links(response)
            if item_links:
                for link in item_links:
                    yield scrapy.Request(url=link.url, callback=self.parse_detail,
                                         meta={'dont_redirect': False, 'handle_httpstatus_list': [302]})
                    # yield scrapy.Request(url=link.url, callback=self.parse_detail)
            # 提取出下一页url
            next_url = response.xpath("//a[@class='load-more']/@href").extract_first()
            if next_url:
                yield scrapy.Request(url=next_url)

    @staticmethod
    def _parse_category1(parsing_rule_dict, response):
        """ 解析 essay
        :param parsing_rule_dict:
        :param response:
        :return:各字段组成的字典
        """
        title = response.xpath(parsing_rule_dict.get("title")).extract_first()
        description = response.xpath(parsing_rule_dict.get("description")).extract_first()
        author = response.xpath(parsing_rule_dict.get("author")).extract()
        author = ';'.join(author)
        published_time = response.xpath('/html').re_first(parsing_rule_dict.get("published_time"))
        if not published_time:
            published_time = response.xpath(parsing_rule_dict.get("publish_time")).extract_first()
        published_time = re.search('\d+-\d+-\d+.*?\d+:\d+:\d+.*?', published_time).group()
        if published_time:
            published_time = re.sub('[^\d\-:]+', ' ', published_time, re.S)
            publish_time = datetime.datetime.strptime(published_time, '%Y-%m-%d %H:%M:%S')
        else:
            publish_time = None
        content = response.xpath(parsing_rule_dict.get("content")).extract_first()
        if content:
            # 替换字符串(末尾)
            content = content.replace('<section class="author">', '￥')
            content = re.search('[\s\S]+<section class="info">[\s\S]+</section>([\s\S]+)￥?', content)
            if content:
                content = ''.join(content.group(1))
            else:
                content = None
        else:
            content = None
        data = {
            "title": title,
            "description": description,
            "author": author,
            "publish_time": publish_time,
            "content": content
        }
        return data

    @staticmethod
    def _parse_category2(parsing_rule_dict, response):
        """解析 除essay、experts
        :param parsing_rule_dict:
        :param response:
        :return: 各字段组成的字典
        """
        title = response.xpath(parsing_rule_dict.get("title")).extract_first()
        published_time = response.xpath('/html').re_first(parsing_rule_dict.get("published_time"))
        if not published_time:
            published_time = response.xpath(parsing_rule_dict.get("publish_time")).extract_first()
        published_time = re.search('\d+-\d+-\d+.*?\d+:\d+:\d+.*?', published_time).group()
        if published_time:
            published_time = re.sub('[^\d\-:]+', ' ', published_time, re.S)
            publish_time = datetime.datetime.strptime(published_time, '%Y-%m-%d %H:%M:%S')
        else:
            publish_time = None
        content = response.xpath(parsing_rule_dict.get("content")).extract_first()
        description = response.xpath(parsing_rule_dict.get("description")).extract_first()
        topic = response.xpath(parsing_rule_dict.get("topic")).extract()
        topic = ';'.join(topic)
        keywords = response.xpath(parsing_rule_dict.get("keywords")).extract()
        keywords = ';'.join(keywords)
        author = response.xpath(parsing_rule_dict.get("author")).extract()
        author = ';'.join(author)
        pdf_urls = response.xpath(parsing_rule_dict.get("pdf_file")).extract()
        pdf_file_dict = {'附件': pdf_urls}
        if pdf_file_dict.get('附件'):
            pdf_file = json.dumps(pdf_file_dict, ensure_ascii=False)
        else:
            pdf_file = None

        if response.url == 'https://www.brookings.edu/events/a-discussion-with-rep-mac-thornberry-on-military-readiness-modernization-and-innovation/':
            print('hello world')

        data = {
            "title": title,
            "publish_time": publish_time,
            "content": content,
            "description": description,
            "topic": topic,
            "keywords": keywords,
            "author": author,
            "pdf_file": pdf_file
        }
        return data

    def _get_item_data(self, category, parsing_rule_dict, response):
        """解析非专家页面
        :param category: 种类
        :param parsing_rule_dict: 对应的解析规则字典
        :param reponse: 该页面响应
        :return: 各字段构造成的字典
        """
        if category == "essay":
            data = self._parse_category1(parsing_rule_dict, response)
        else:
            data = self._parse_category2(parsing_rule_dict, response)
        data['category'] = category
        data['url'] = response.url
        return data

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

        # 附件
        pdf_urls = response.xpath(parsing_rule_dict.get("pdf_file")).extract()
        pdf_file_dict = {"附件": []}
        for i in range(len(pdf_urls)):
            annex_dict = dict()
            annex_dict["附件{}".format(i + 1)] = pdf_urls[i]
            pdf_file_dict["附件"].append(annex_dict)
        if pdf_file_dict.get("附件"):
            pdf_file = json.dumps(pdf_file_dict, ensure_ascii=False)
        else:
            pdf_file = ''
        # 联系方式
        contact = dict()
        contact_selectors = response.xpath(parsing_rule_dict.get("contact"))
        for selector in contact_selectors:
            contact[selector.xpath("./@itemprop")] = contact[selector.xpath("./@href")]

        # 活跃的媒体
        active_media_dict = dict()
        active_media_selectors = response.xpath(parsing_rule_dict.get("active_media"))
        for media in active_media_selectors:
            active_media_dict[media.xpath("./@class")] = media.xpath("./@href")
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

    def parse_detail(self, response):
        external_url = response.headers.get("Location")
        if external_url:
            external_url = external_url.decode()
        if response.status == 302:
            data = {"status_code": response.status, "internal_url": response.url, "external_url": external_url}
            item = AbandonItem(**data)
            yield item
        else:
            category = re.search('.*?brookings.edu/(.*?)/\S+', response.url)
            if category:
                category = category.group(1)
                parsing_rule_dict = parsing_rules.get(category)
                if category in parsing_rules and category != "experts":  # 非专家
                    data = self._get_item_data(category, parsing_rule_dict, response)
                    item = SearchItem(**data)
                    yield item
                elif category in parsing_rules and category == "experts":  # 专家
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
