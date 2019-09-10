# -*- coding: utf-8 -*-

class UsCfrSpider:
    def __init__(self, *args, **kwargs):
        pass


class Test(UsCfrSpider):
    def __init__(self, keyword='beijing', page_size=10, *args, **kwargs):
        super(UsCfrSpider, self).__init__(*args, **kwargs)
        self.keyword = keyword
        self.page_size = page_size


if __name__ == '__main__':
    test = Test(keyword='hello world', page_size=50)
    print(test.keyword)
    print(test.page_size)
