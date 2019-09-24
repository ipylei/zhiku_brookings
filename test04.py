# -*- coding: utf-8 -*-

import re

url = 'https://www.brookings.edu/wp-content/uploads/2016/05/cv_aaron_12018.p2df'

if re.search('pdf$', url):
    print(url)
else:
    print('hello world')
