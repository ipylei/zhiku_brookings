# -*- coding: utf-8 -*-

# TODO "datePublished":"2012-04-29T19:41:29Z",
import datetime
import re

# string = response.body.decode('utf-8')

# string = """
# dateCreated":"2012-04-29T18:56:20Z","datePublished":"2012-04-29T18:56:20Z","dateModified":"2016-07-29T08:59:22Z","articleSection":"Health Care Policy","author":[],"creator":[],"publisher":{"@type":"Organization","name":"Brookings","logo":{"@type":"ImageObject","url":"https:\/\/www.brookings.edu\/wp-content\/themes\/brookings\/static\/images\/brookings-logo.jpg","height":"60","width":"400"}}
# ,"keywords":["","english","health care policy","medicare &amp; medicaid","center for health policy","en"]}
# """
#
# search_publish_time = re.search('datePublished":"(\d+-\d+-\d+T\d+:\d+:\w+)",', string, re.S)
# if search_publish_time:
#     u_time = search_publish_time.group(1)
#     published_time = re.search('\d+-\d+-\d+.*?\d+:\d+:\d+.*?', u_time).group()
#     published_time = published_time.replace('T', ' ')
#     publish_time = datetime.datetime.strptime(published_time, '%Y-%m-%d %H:%M:%S')
# else:
#     publish_time = None
# print(publish_time)
# print(type(publish_time))

# published_time = '2019-08-19T10:00:49-04:00'
# published_time = '2019-03-07T05:00:48+00:00'
# published_time = '2012-04-29T19:41:29Z'
published_time = '2012-04-29CST19:41:29Z'
published_time = re.search('\d+-\d+-\d+.*?\d+:\d+:\d+.*?', published_time).group()
# published_time = published_time.replace('T', ' ')
published_time = re.sub('[^\d\-:]+', ' ', published_time, re.S)
# print(published_time)
publish_time = str(datetime.datetime.strptime(published_time, '%Y-%m-%d %H:%M:%S'))
print(publish_time)


# def get_publish_time(method, response):
#     if method == 'xpath':
#         published_time = '2019-08-19T10:00:49-04:00'
#         # published_time = response.xpath("args").extract_first().strip()
#         published_time = re.search('\d+-\d+-\d+.*?\d+:\d+:\d+.*?', published_time).group()
#         published_time = published_time.replace('T', ' ')
#         publish_time = datetime.datetime.strptime(published_time, '%Y-%m-%d %H:%M:%S')
#         return publish_time
#     elif method == 're':
#         # search_publish_time = re.search('datePublished":"(\d+-\d+-\d+T\d+:\d+:\d+Z)",', response.text, re.S)
#         search_publish_time = re.search('datePublished":"(\d+-\d+-\d+T\d+:\d+:\d+Z)",', response, re.S)
#         if search_publish_time:
#             u_time = search_publish_time.group(1)
#             published_time = re.search('\d+-\d+-\d+.*?\d+:\d+:\d+.*?', u_time).group()
#             published_time = published_time.replace('T', ' ')
#             publish_time = datetime.datetime.strptime(published_time, '%Y-%m-%d %H:%M:%S')
#             return publish_time


if __name__ == '__main__':
    # response = string
    # publish_time = get_publish_time('re', response)
    # print(publish_time)
    pass
