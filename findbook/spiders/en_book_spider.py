# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 15:30:36 2018

@author: chris
"""

import scrapy 
import datetime
from scrapy.spiders import CrawlSpider, Rule
from findbook.items import EnBook
from scrapy.utils.project import get_project_settings
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
import logging
logger = logging.getLogger('enSpider')
hdlr = logging.FileHandler(get_project_settings().get('LOGPATH')+"/en/"+datetime.datetime.now().strftime("%Y%m%d")+".log")
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 

class EnBookSpider(CrawlSpider):
    name = "en_book_spider"
    
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES':{
             'scrapy.downloadermiddlewares.retry.RetryMiddleware': 90,
             'scrapy_proxies.RandomProxy': 100,
#            'scrapyjs.SplashMiddleware': 725,
        },
        'ITEM_PIPELINES': {
            'findbook.pipelines.EnBookCrawlerPipeline': 400
        }
    }
        
    def __init__(self):
        logger.info('begin enBook crwaler')
        
        self.settings       = get_project_settings()
        self.FoundBooks     = []
        self.notFoundBooks  = []
        self.settings       = get_project_settings()
        self.proxy_list     = self.settings.get('PROXY_LIST')
        self.proxies        = {}
        self.filePath       = self.settings.get('FILEPATH')
        self.fileName       = self.filePath+'/en/'+datetime.datetime.now().strftime("%Y%m%d")+'.xlsx'
        
        
        dispatcher.connect(self.spider_closed, signals.spider_closed)
    
    def start_requests(self):
        logger.info('begin request')
        searchUrl       = 'https://www.bookdepository.com/search?searchTerm='
        fileNm          = self.settings.get('RECORDPATH')+"/en/"+datetime.datetime.now().strftime("%Y%m%d")+".txt"
        fin             = open(fileNm)
        try:
            for line in fin.readlines():
                isbn = line.strip()
#                print(isbn)
                yield scrapy.Request(url=searchUrl+isbn, callback=self.parse, meta={'isbn':isbn})      
        finally:
            fin.close()        
        
    def parse(self, response):
        logger.info('begin parse item')
        isbn                = response.request.meta['isbn']
        title               = response.xpath('//div[@class="item-info"]/h1/text()').extract_first()
        price               = response.xpath('//span[@class="list-price"]/text()').re_first(r'NT\$\s*(.*)')  
        if price is None: 
            price = response.xpath('//span[@class="sale-price"]/text()').re_first(r'NT\$\s*(.*)')  
        if title is not None:
            self.FoundBooks.append(isbn);
            book                = EnBook()
            book['url']         = response.url
            book['title_main']  = title
            book['picture']     = response.xpath('//div[@class="item-img-content"]/img/@src').extract_first()
            book['author']      = response.xpath('//div[@class="author-info hidden-md"]/a[@itemprop="author"]/text()').extract_first()
            book['publisher']   = response.xpath('//ul[@class="biblio-info"]/li/span/a[@itemprop="publisher"]/text()').extract_first().replace('\n', '').strip()
            categorys           = response.xpath('//ol[@class="breadcrumb"]/li/a/text()')
            cats                = ''
            for index, cat in enumerate(categorys):
                cats += cat.extract().replace('\n', '').strip() + "/"
            book['category']    = cats
            book['isbn13']      = response.xpath('//ul[@class="biblio-info"]/li/span[@itemprop="isbn"]/text()').extract_first()
            book['price_org']   = price
            book['price_twd']   = int(price.replace(',', ''))
            book['sale_date']   = response.xpath('//ul[@class="biblio-info"]/li/span[@itemprop="datePublished"]/text()').extract_first().replace('\n', '').strip()
            book['content']     = response.xpath('//div[@class="item-excerpt trunc"]/text()').extract_first()
            yield book
        else:
            self.notFoundBooks.append(isbn);
    def spider_closed(self, spider):
        logger.info('spider closed')
        logger.info('book found length:'+str(len(self.FoundBooks)))
        logger.info('book not found length:'+str(len(self.notFoundBooks)))
        
        
            