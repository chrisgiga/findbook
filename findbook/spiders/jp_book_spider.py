# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 17:12:30 2018

@author: taaze
"""
import scrapy
import datetime
from scrapy.spiders import CrawlSpider, Rule
from findbook.items import JpBook
from scrapy.utils.project import get_project_settings
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
import logging

logger = logging.getLogger('jpSpider')
hdlr = logging.FileHandler(get_project_settings().get('LOGPATH')+"/jp/"+datetime.datetime.now().strftime("%Y%m%d")+".log")
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 

class JpBookSpider(CrawlSpider):
    name            = "jp_book_spider"
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES':{
             'scrapy.downloadermiddlewares.retry.RetryMiddleware': 90,
             'scrapy_proxies.RandomProxy': 100,
#            'scrapyjs.SplashMiddleware': 725,
        },
        'ITEM_PIPELINES': {
            'findbook.pipelines.JpBookCrawlerPipeline': 400
        }
    }
    
    def __init__(self):
        logger.info('begin jpBook crwaler')
        self.settings       = get_project_settings()
        self.FoundBooks     = []
        self.notFoundBooks  = []
        self.proxy_list     = self.settings.get('PROXY_LIST')
        self.proxies        = {}
        self.filePath       = self.settings.get('FILEPATH')
        self.fileName       = self.filePath+'/jp/'+datetime.datetime.now().strftime("%Y%m%d")+'.xlsx'
        
        dispatcher.connect(self.spider_closed, signals.spider_closed)
    
    
    def start_requests(self):
        logger.info('begin request')
        searchUrl       = 'https://honto.jp/netstore/search.html?k='
        fileNm          = self.settings.get('RECORDPATH')+"/jp/"+datetime.datetime.now().strftime("%Y%m%d")+".txt"
        fin             = open(fileNm)
        try:
            for line in fin.readlines():
                isbn = line.strip()
#                print(isbn)
                yield scrapy.Request(url=searchUrl+isbn, callback=self.parse_list, meta={'isbn':isbn})      
        finally:
            fin.close()      
            
    def parse_list(self, response):
        logger.info('begin parse list')
        isbn    = response.request.meta['isbn']
        url     = response.xpath('//div[@id="displayOrder1"]/div/div[@class="stInfo"]/div[@class="stImg"]/p/a/@href').extract_first()
#        return [scrapy.FormRequest(urls.extract_first(), 
#                                   callback=self.parse)] 
        if url is not None:
            yield scrapy.Request(url=url, callback=self.parse , meta={'isbn':isbn})    
        else:
            self.notFoundBooks.append(isbn)
            
    def parse(self, response):
        isbn                = response.request.meta['isbn']
        self.FoundBooks.append(isbn)
        book                = JpBook()
        book['url']         = response.url
        book['picture']     = response.xpath('//div[@class="stContents"]/div[@class="stImg"]/div[@class="stPhoto"]/div[@class="stCover"]/a/img/@src').extract_first()
        if response.xpath('//p[@class="stFormat stEb"]/text()').extract_first() == "電子書籍":
            book['title_main']  = response.xpath('//div[@class="stTitle"]/p[@class="stTitle"]/text()').extract_first()
        else:
            book['title_main']  = response.xpath('//div[@class="stOverview"]/h1[@class="stTitle"]/text()').extract_first()
        book['author']      = response.xpath('//div[@class="stOverview"]/p[@class="stAuthor"]/span[2]/a/text()').re_first(r'\s*(.*)（著）')
        book['content']     = response.xpath('//div[@id="productInfomation"]/div[@class="stView"]/div[@class="stContents"]/p/text()').extract_first()
        stItems             = response.xpath('//div[@class="stLeftArea"]/div[@class="stExtra"]/ul[@class="stItemData"]/li')
        sale_date           = ""
        product_type        = ""
        publisher           = ""
        for index, item in enumerate(stItems):
            str = item.extract()
            if "発行年月：" in str: 
                sale_date           = item.xpath('text()').re_first('発行年月：\s*(.*)')
#                book['sale_date']   = item.xpath('text()').re_first('発行年月：\s*(.*)')
            if "取扱開始日：" in str:
                sale_date           = item.xpath('text()').re_first('取扱開始日：\s*(.*)')
#                book['sale_date']   = item.xpath('text()').re_first('取扱開始日：\s*(.*)')
            if "販売開始日：" in str:
                sale_date           = item.xpath('text()').re_first('販売開始日：\s*(.*)')
#                book['sale_date']   = item.xpath('text()').re_first('販売開始日：\s*(.*)')
            if "カテゴリ：" in str:
                product_type        = item.xpath('text()').re_first('カテゴリ：\s*(.*)')
#                book['type']        = item.xpath('text()').re_first('カテゴリ：\s*(.*)')
            if "出版社：" in str:
                publisher           = item.xpath('a/text()').extract_first()
#                book['publisher']   = item.xpath('a/text()').extract_first()
#        book['publisher']   = response.xpath('//div[@class="stLeftArea"]/div[@class="stExtra"]/ul[@class="stItemData"]/li[3]/a/text()').extract_first()
#        book['sale_date']   = response.xpath('//div[@class="stLeftArea"]/div[@class="stExtra"]/ul[@class="stItemData"]/li[2]/text()').re_first('発行年月：\s*(.*)')
        book['sale_date']   = sale_date
        book['type']        = product_type
        book['publisher']   = publisher
        cat0                = response.xpath('//div[@id="stTopicPath"]/ol/li[3]/a/text()').extract_first() 
        cat1                = response.xpath('//div[@id="stTopicPath"]/ol/li[4]/a/text()').extract_first() 
        book['category']    = cat0 + " " + cat1
        book['isbn']        = isbn
        price               = response.xpath('//div[@class="stCart01"]/div/div[@class="stHeading"]/div[@class="stPrice"]/div[@class="stPriceInner"]/span[@class="stPrice"]/text()').extract_first()
        book['price']       = price
        book['page']        = ""
        book['ean']         = isbn
        book['price_twd']   = round(int(price.replace(',', ''))/4)
        yield book  
        
    def spider_closed(self, spider):
        orcl    = None
        curs    = None
        logger.info('spider closed')
        logger.info('book found length:'+str(len(self.FoundBooks)))
        logger.info('book not found length:'+str(len(self.notFoundBooks)))
        
    