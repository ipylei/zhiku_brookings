# -*- coding: utf-8 -*-
import json
import re
import datetime
import time

import scrapy
from scrapy.linkextractors import LinkExtractor

from brookings.config import parsing_rules
from brookings.items import SearchItem, ExpertItem, AbandonItem, ExpertContactItem
from brookings.settings import WEBSITE


class SearchSpider(scrapy.Spider):
    name = 'search_spider'
    page_count = 0
    basic_url = 'https://www.brookings.edu/search/?s={}'

    # allowed_domains = ['brookings.edu']

    def __init__(self, name=None, **kwargs):
        super(SearchSpider, self).__init__(name, **kwargs)
        self.keyword = kwargs.get('keyword') if kwargs.get('keyword') else 'news'
        self.page_size = kwargs.get('page_size') if kwargs.get('page_size') else 10

    def start_requests(self):
        start_url = self.basic_url.format(self.keyword)
        yield scrapy.Request(url=start_url)

    def parse(self, response):
        """解析列表页
        :param response:
        :return:
        """
        self.page_count += 1
        if self.page_count <= self.page_size:
            # 提取详情url
            item_selectors = response.xpath("//div[@class='list-content']/article")
            if item_selectors:
                for selector in item_selectors:
                    url = selector.xpath(".//h4[@class='title']/a/@href").extract_first()
                    data_source = selector.xpath(".//a[@class='label']/text()").extract_first()
                    yield scrapy.Request(url=url, callback=self.parse_detail,
                                         meta={'dont_redirect': False,
                                               'handle_httpstatus_list': [302],
                                               'data_source': data_source
                                               })
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
        author = ','.join(author)
        published_time = response.xpath('/html').re_first(parsing_rule_dict.get("published_time"))
        if not published_time:
            published_time = response.xpath(parsing_rule_dict.get("publish_time")).extract_first()
        published_time = re.search('\d+-\d+-\d+.*?\d+:\d+:\d+.*?', published_time).group()
        if published_time:
            published_time = re.sub('[^\d\-:]+', ' ', published_time, re.S)
            publish_time = str(datetime.datetime.strptime(published_time, '%Y-%m-%d %H:%M:%S'))
        else:
            publish_time = ""
        content = response.xpath(parsing_rule_dict.get("content")).extract_first()
        if content:
            # 替换字符串(末尾)
            content = content.replace('<section class="author">', '￥')
            content = re.search('[\s\S]+<section class="info">[\s\S]+</section>([\s\S]+)￥?', content)
            if content:
                content = ''.join(content.group(1))
            else:
                content = ""
        else:
            content = ""
        data = {
            "Title": title if title else title,
            "Author": author if author else author,
            "PublishTime": publish_time if publish_time else publish_time,
            "Keywords": "",
            "Abstract": description if description else description,
            "Content": content if content else content,
            "topic": "",
            "tags": "",
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
            publish_time = str(datetime.datetime.strptime(published_time, '%Y-%m-%d %H:%M:%S'))
        else:
            publish_time = ""
        content = response.xpath(parsing_rule_dict.get("content")).extract_first()
        description = response.xpath(parsing_rule_dict.get("description")).extract_first()
        topic = response.xpath(parsing_rule_dict.get("topic")).extract()
        topic = ','.join(topic)
        keywords = response.xpath(parsing_rule_dict.get("keywords")).extract()
        keywords = ','.join(keywords)
        author = response.xpath(parsing_rule_dict.get("author")).extract()
        author = ','.join(author)
        pdf_urls = response.xpath(parsing_rule_dict.get("pdf_file")).extract()
        pdf_file_dict = {'附件': pdf_urls}
        if pdf_file_dict.get('附件'):
            pdf_file = json.dumps(pdf_file_dict, ensure_ascii=False)
        else:
            pdf_file = ""

        data = {
            "Title": title if title else "",
            "Author": author if author else author,
            "PublishTime": publish_time if publish_time else "",
            "Keywords": keywords if keywords else "",
            "Abstract": description if description else "",
            "Content": content if content else "",
            "topic": topic if topic else "",
            "tags": "",
            "pdf_file": pdf_file
        }
        return data

    def _get_item_data(self, category, parsing_rule_dict, response):
        """解析非专家页面
        :param category: 种类
        :param parsing_rule_dict: 对应的解析规则字典
        :param response: 该页面响应
        :return: 各字段构造成的字典
        """
        if category == "essay":
            data = self._parse_category1(parsing_rule_dict, response)
        else:
            data = self._parse_category2(parsing_rule_dict, response)
        data['Url'] = response.url
        data['Category'] = category
        data['site_name'] = WEBSITE
        return data

    @staticmethod
    def _get_experts_data(parsing_rule_dict, response):
        """解析专家页面
        :return: 各字段构造成的字典
        """
        name = response.xpath(parsing_rule_dict.get("name")).extract_first()
        head_portrait = response.xpath(parsing_rule_dict.get("head_portrait")).extract_first()
        brief_introd = response.xpath(parsing_rule_dict.get("brief_introd")).extract_first()
        jobs = response.xpath(parsing_rule_dict.get("job")).extract()
        job = [job.replace('-', '') for job in jobs]
        job = ','.join(job)
        research_field = response.xpath(parsing_rule_dict.get("research_field")).extract()
        research_field = ','.join(research_field)
        education = response.xpath(parsing_rule_dict.get("education")).extract()
        education = ','.join(education)

        # 附件
        # pdf_urls = response.xpath(parsing_rule_dict.get("pdf_file")).extract()
        # pdf_file_dict = {'附件': pdf_urls}
        # if pdf_file_dict.get('附件'):
        #     pdf_file = json.dumps(pdf_file_dict, ensure_ascii=False)
        # else:
        #     pdf_file = None

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
            active_media = ','.join(active_media_dict.values())
            # active_media = json.dumps(active_media_dict, ensure_ascii=False)
        else:
            active_media = ''

        # expert_grid_selectors = response.xpath(parsing_rule_dict.get("expert-grid"))
        # try:
        #     topics_string = expert_grid_selectors.xpath('//dl').re_first(
        #         '<dt>[\s\S]*?Topics[\s\S]*?</dt>([\s\S]*?)<dt>')
        #     topics = ';'.join(re.findall('<dd><.*?>([\s\S]*?)<.*?></dd>', topics_string, re.S))
        # except:
        #     topics = ''
        # try:
        #     centers_string = expert_grid_selectors.xpath('//dl').re_first(
        #         '<dt>[\s\S]*?Centers[\s\S]*?</dt>([\s\S]*?)<dt>')
        #     centers = ';'.join(re.findall('<dd><.*?>([\s\S]*?)<.*?></dd>', centers_string, re.S))
        # except:
        #     centers = ''
        # try:
        #     projects_string = expert_grid_selectors.xpath('//dl').re_first(
        #         '<dt>[\s\S]*?Projects[\s\S]*?</dt>([\s\S]*?)<dt>')
        #     projects = ';'.join(
        #         re.findall('<dd><.*?>([\s\S]*?)<.*?></dd>', projects_string, re.S)) if projects_string else ''
        # except:
        #     projects = ''
        # try:
        #     addition_areas_string = expert_grid_selectors.xpath('//dl').re_first(
        #         '<dt>[\s\S]*?Additional Expertise Areas[\s\S]*?</dt>([\s\S]*?)<dt>')
        #     addition_areas = ';'.join(
        #         re.findall('<dd>([\s\S]*?)</dd>', addition_areas_string, re.S)) if addition_areas_string else ''
        # except:
        #     addition_areas = ''
        # try:
        #     current_positions_string = expert_grid_selectors.xpath('//dl').re_first(
        #         '<dt>[\s\S]*?Current Positions[\s\S]*?</dt>([\s\S]*?)<dt>')
        #     current_positions = ';'.join(
        #         re.findall('<dd>([\s\S]*?)</dd>', current_positions_string, re.S)) if current_positions_string else ''
        # except:
        #     current_positions = ''
        # try:
        #     past_positions_string = expert_grid_selectors.xpath('//dl').re_first(
        #         '<dt>[\s\S]*?Past Positions[\s\S]*?</dt>([\s\S]*?)<dt>')
        #     past_positions = ';'.join(
        #         re.findall('<dd>([\s\S]*?)</dd>', past_positions_string, re.S)) if past_positions_string else ''
        # except:
        #     past_positions = ''
        # try:
        #     languages_string = expert_grid_selectors.xpath('//dl').re_first(
        #         '<dt>[\s\S]*?Language Fluency[\s\S]*?</dt>([\s\S]*?)<dt>')
        #     languages = ';'.join(re.findall('<dd>([\s\S]*?)</dd>', languages_string, re.S))
        # except:
        #     languages = ''

        last_dt_content = response.xpath(
            "//div[@class='expert-grid']/dl/dt[last()]/following-sibling::dd/text()").extract()
        last_dt_content = ','.join(last_dt_content)
        last_dt_field = response.xpath("//div[@class='expert-grid']/dl/dt[last()]/text()").extract_first()
        if last_dt_field:
            last_dt_field = last_dt_field.strip().replace('"', '')
        # if last_dt_field == 'Contact':  # 联系方式不在此列
        #     last_dt_field = None
        # elif last_dt_field == 'Topics':
        #     last_dt_field = "topics"
        # elif last_dt_field == "Centers":
        #     last_dt_field = "centers"
        # elif last_dt_field == 'Projects':
        #     last_dt_field = "projects"
        # elif last_dt_field == 'Additional Expertise Areas':
        #     last_dt_field = "addition_areas"
        # elif last_dt_field == 'Current Positions':
        #     last_dt_field = "current_positions"
        # elif last_dt_field == 'Past Positions':
        #     last_dt_field = "past_positions"
        if last_dt_field == 'Education':
            last_dt_field = "education"
        # elif last_dt_field == 'Language Fluency':
        #     last_dt_field = "languages"
        else:  # 其他不知名的不在此列
            last_dt_field = None

        data = {
            "name": name,
            "experts_url": response.url,
            "img_url": head_portrait if head_portrait else "",
            "abstract": brief_introd if brief_introd else "",
            "research_field": research_field if research_field else "",
            "job": job if job else "",
            "education": education if education else "",
            "contact": [contact] if contact else "",
            "reward": "",
            "active_media": active_media if active_media else "",
            "relevant": "",
            # "createTime": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),
            # "pdf_file": pdf_file,
        }
        if last_dt_field:
            last_dt_field_dict = {last_dt_field: last_dt_content}
            data.update(last_dt_field_dict)
        return data

    def parse_detail(self, response):
        # external_url = response.headers.get("Location")
        # if external_url:
        #     external_url = external_url.decode()
        # if response.status == 302:
        #     data = {"status_code": response.status, "internal_url": response.url, "external_url": external_url}
        #     item = AbandonItem(**data)
        #     yield item
        if response.status == 200:
            category = re.search('.*?brookings.edu/(.*?)/\S+', response.url)
            if category:
                category = category.group(1)
                parsing_rule_dict = parsing_rules.get(category)
                if category in parsing_rules and category != "experts":  # 非专家
                    data = self._get_item_data(category, parsing_rule_dict, response)
                    data["DataSource"] = response.meta.get("data_source")
                    item = SearchItem(**data)
                    yield item
                elif category in parsing_rules and category == "experts":  # 专家
                    data = self._get_experts_data(parsing_rule_dict, response)
                    # contacts = data.pop("contact")
                    item = ExpertItem(**data)
                    # for key, value in contacts.items():
                    #     contact_data = {"url": response.url, "name": data.get("name"), "type": key, "contact": value}
                    #     item2 = ExpertContactItem(**contact_data)
                    #     yield item2  # 联系方式
                    yield item
                # else:  # category未在解析规则中
                #     data = {"status_code": response.status, "internal_url": response.url, "external_url": external_url}
                #     item = AbandonItem(**data)
                #     yield item
            # else:  # 没有category的情况
            #     data = {"status_code": response.status, "internal_url": response.url, "external_url": external_url}
            #     item = AbandonItem(**data)
            #     yield item
        # else:  # 其他响应码
        #     data = {"status_code": response.status, "internal_url": response.url, "external_url": external_url}
        #     item = AbandonItem(**data)
        #     yield item
