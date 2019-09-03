# -*- coding: utf-8 -*-


import re

# url = 'https://www.brookwings.edu/events/central-american-workshop-on-human-rights-in-disaster-management/'
# url = 'https://www.brookings.edu/events/central-american-workshop-on-human-rights-in-disaster-management/'
# url = 'https://www.brookings.edu/blog/fixgov/2019/08/20/americans-want-federal-action-on-election-security-ahead-of-2020-per-new-brookings-survey/'
# url = 'https://www.brookings.edu/interactives/red-sea-rivalries/'
# url = 'https://www.brookings.edu/opinions/despite-scary-headlines-americas-elderly-continue-to-prosper/'
# url = 'https://www.brookings.edu/testimonies/how-the-small-businesses-investment-company-program-can-better-support-americas-advanced-industries/'
url = 'https://www.brookings.edu/experts/henry-j-aaron/'
topic = re.search('.*?brookings.edu/(.*?)/\S+', url)
if topic:
    topic = topic.group(1)
    print(topic)
else:
    print('----')

