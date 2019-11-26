# -*- coding: utf-8 -*-

# Scrapy settings for brookings project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html


BOT_NAME = 'brookings'

SPIDER_MODULES = ['brookings.spiders']
NEWSPIDER_MODULE = 'brookings.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'brookings (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
# }

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'brookings.middlewares.BrookingsSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
#    'brookings.middlewares.BrookingsDownloaderMiddleware': 543,
# }

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'brookings.pipelines.BrookingsPipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'


FEED_EXPORT_ENCODING = 'utf-8'

# 日志配置
# 是否启用日志
LOG_ENABLED = True
# 日志使用的编码
LOG_ENCODING = 'utf-8'
# 日志文件(文件名)
# LOG_FILE = './log.txt'
LOG_FILE = None
# 日志格式
LOG_FORMAT = '%(asctime)s [%(name)s] %(levelname)s: %(message)s'
# 日志时间格式
LOG_DATEFORMAT = '%Y-%m-%d %H:%M:%S'
# 日志级别 CRITICAL, ERROR, WARNING, INFO, DEBUG
LOG_LEVEL = 'DEBUG'
# 如果等于True，所有的标准输出（包括错误）都会重定向到日志，例如：print('hello')
LOG_STDOUT = False
# 如果等于True，日志仅仅包含根路径，False显示日志输出组件
LOG_SHORT_NAMES = False

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36'
# DEFAULT_REQUEST_HEADERS = {}

# REDIRECT_ENABLED = False # 禁止重定向
# HTTPERROR_ALLOWED_CODES = [301, 302]

# 数据库配置
MYSQL_HOST = '127.0.0.1'
MYSQL_DATABASE = 'zhiku'
MYSQL_PORT = 3306
MYSQL_USERNAME = 'root'
MYSQL_PASSWORD = '123456'

# RabbiMQ配置
# MQ_HOST = '10.4.7.44'
# MQ_HOST = '127.0.0.1'
# MQ_USERNAME = 'guest'
# MQ_PASSWORD = 'guest'

# MQ_HOST = '10.4.9.177'
# MQ_HOST = '47.74.153.83'
# MQ_USERNAME = 'admin'
# MQ_PASSWORD = '123456'
# MQ_PORT = 5672

MQ_NEWS_QUEUE = 'zk_news'  # 新闻队列
MQ_EXPERT_QUEUE = 'zk_experts'  # 专家队列
MQ_FILE_QUEUE = 'zk_file_task_queue'  # 附件队列
MQ_IMAGE_QUEUE = 'zk_img_task_queue'  # 内容图片队列
MQ_EXPERT_IMG_QUEUE = 'zk_expert_img_task_queue'  # 专家头像队列
MQ_SWITCH = True  # 是否推入MQ

WEBSITE = '布鲁金斯学会'
