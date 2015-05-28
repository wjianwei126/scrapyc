from scrapy.utils.response import get_base_url
from w3lib.url import urljoin_rfc

from scrapy import signals
from robot.items import NimeiItem
import scrapy

class Parser(object):
    """docstring for Parser"""
    def __init__(self, spider):
        super(Parser, self).__init__()
        self.spider = spider

    def parse(self,response):

        base_url  = get_base_url(response)
        for sel in response.xpath('//a/@href')[1:]:
            relative_url = sel.extract()
            abs_url =urljoin_rfc(base_url,relative_url)
                #print abs_url
            #schema = get_url_scheme(abs_url)
            # if schema not in ["http","https"]:
            #     continue
            if abs_url[-1] == "/":
                yield scrapy.Request(abs_url,callback=self.parse)
            else:
                yield NimeiItem(url=abs_url,furl=response.url)    


            