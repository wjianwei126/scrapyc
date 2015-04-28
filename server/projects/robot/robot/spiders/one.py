import scrapy
from scrapy.utils.response import get_base_url
from w3lib.url import urljoin_rfc

from scrapy import signals
from robot.items import NimeiItem

def get_url_site(url):
    if "://" in url:
        purl = url.split('://',1)[1]
    else:
        purl = url
    return purl.split("/",1)[0]

def get_url_scheme(url):
    if ":" in url[:11]:
        return  url.split(':',1)[0]
    else:
        return "http"


class RobotSpider(scrapy.Spider):
    name = "one"
    allowed_domains = []
    start_urls = [    ]
    def __init__(self,*args, **kwargs):
        super(RobotSpider, self).__init__(*args, **kwargs)
        self._kwargs = kwargs

    def start_requests(self):
        self.crawler.signals.connect(self.spider_idle,signals.spider_idle)
        fname = self.settings.get("INPUT_FILE",None)
        if fname:
            with open(fname) as fh:
                for line in fh.readlines():
                    url = line.strip().split()[0]
                    req =  scrapy.Request(url,callback=self.parse)
                    yield req
        for url in self.start_urls:
            req =  scrapy.Request(url,callback=self.parse)
            #req.meta["depth"] =  1
            yield req            
        pass
    def parse(self, response):
        self.log("Crawled %s %d"%(response.url,response.status),level=scrapy.log.INFO)
        #self.log("Crawled (%d) <GET %s>"%(response.status,response.url),level=scrapy.log.INFO)
        base_url  = get_base_url(response)
        # if "depth" in response.meta:
        #     depth = response.meta["depth"]
        # else:
        #     depth = 1
        MAX_DEPTH =  self.settings.get("MAX_DEPTH",1)
        ALLOW_SITES = self.settings.get("ALLOW_SITES",[])
        base_site = get_url_site(response.url)
        for sel in response.xpath('//a/@href'):
            relative_url = sel.extract()
            abs_url =urljoin_rfc(base_url,relative_url)
            #print abs_url
            site = get_url_site(abs_url)
            yield NimeiItem(url=abs_url,furl=response.url)
            if site != base_site and site not in ALLOW_SITES:
                continue
            schema = get_url_scheme(abs_url)
            if schema not in ["http","https"]:
                continue
            yield scrapy.Request(abs_url,callback=self.parse)
            # if depth < MAX_DEPTH:
            #     req =  scrapy.Request(abs_url,callback=self.parse)
            #     req.meta["depth"] = depth + 1
            #     yield req

    def spider_idle(self,spider):

        if spider==self:
            return False
        return True
