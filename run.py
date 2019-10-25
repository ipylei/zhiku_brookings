# -*- coding: utf-8 -*-
from scrapy import cmdline

# cmdline.execute('scrapy crawl search_spider -o result.json'.split())
# cmdline.execute('scrapy crawl expert_spider -o result.json'.split())

# cmdline.execute('scrapy crawl spider_expert'.split())
cmdline.execute('scrapy crawl spider_search'.split())
