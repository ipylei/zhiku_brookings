# -*- coding: utf-8 -*-

parsing_rule_experts = {
    "expert-grid": "//div[@class='expert-grid']",
    "name": "//h1[@class='name']/text()",
    "head_portrait": "//div[@class='expert-image']/img/@src",
    "brief_introd": "//div[@itemprop='description']",
    "job": "//div[@class='expert-info']//h3[@class='title']/text()",
    "research_field": "//div[@class='expert-info']//h3[@class='title']/a/text()",
    "education": "//dt[contains(text(),'Education')]/following-sibling::dd/text()",
    "contact": "//div[@class='expert-grid']//dd[@class='expert-contact']//a/@href | //div[@class='expert-grid']//dd//a[@class='number']/@href",
    "pdf_file": "//p[@class='download-cta']/following-sibling::*//li//a/@href",
}
parsing_rule_events = {
    "title": "//h1[@itemprop='name']/text() | //div[@class='headline-wrapper']//h1[@class='report-title']/text() | //meta[@property='og:title']/@content",
    "published_time": '"datePublished":"(\d+-\d+-\d+T\d+:\d+:\w+)",',
    "publish_time": "//time[@class='date']/@content | //meta[@property='article:published_time']/@content",
    "content": "//div[@class='event-description post-body'] | //div[@itemprop='description'] | //div[@itemprop='articleBody'] | //div[@class='post-body post-body-enhanced']",
    "description": "//meta[@property='og:description']/@content | //meta[@name='description']/@content",
    "topic": "//section[@class='related-topics']//ul//a[@class='tag']/text()",
    "keywords": "//meta[@name='keywords']/@content",
    "author": "//div[@class='inline-widget-inner']//span[@itemprop='name']/text()",
    "pdf_file": "//p[@class='download-cta']/following-sibling::*//li//a/@href",
}
parsing_rule_blog = parsing_rule_events
parsing_rule_book = parsing_rule_events
parsing_rule_bpea_articles = parsing_rule_events
parsing_rule_essay = {
    "title": "//h1[@class='header__title'] | //meta[@property='og:title']/@content",
    "published_time": '"datePublished":"(\d+-\d+-\d+T\d+:\d+:\w+)",',
    "publish_time": "//meta[@property='article:published_time']/@content",
    "content": "//div[contains(@id,'tbe')]",
    "description": "//meta[@property='og:description']/@content | //meta[@name='description']/@content",
    "author": "//section[@class='author']//a/strong/text()"
}
parsing_rule_interactives = parsing_rule_events
parsing_rule_on_the_record = parsing_rule_events
parsing_rule_opinions = parsing_rule_events
parsing_rule_podcast_episode = parsing_rule_events
parsing_rule_product = parsing_rule_events
parsing_rule_research = parsing_rule_events
parsing_rule_testimonies = parsing_rule_events

parsing_rules = {
    "experts": parsing_rule_experts,
    "events": parsing_rule_events,
    "blog": parsing_rule_blog,
    "book": parsing_rule_book,
    "essay": parsing_rule_essay,
    "bpea-articles": parsing_rule_bpea_articles,
    "interactives": parsing_rule_interactives,
    "on-the-record": parsing_rule_on_the_record,
    "opinions": parsing_rule_opinions,
    "podcast-episode": parsing_rule_podcast_episode,
    "product": parsing_rule_product,
    "research": parsing_rule_research,
    "testimonies": parsing_rule_testimonies
}
