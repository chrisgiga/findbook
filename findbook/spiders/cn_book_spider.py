# -*- coding: utf-8 -*-
"""
Created on Thu Feb  1 15:54:10 2018

@author: chris
"""
import scrapy 
import re
import datetime
from scrapy.spiders import CrawlSpider, Rule
from findbook.items import CnBook
from scrapy.utils.project import get_project_settings
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
import logging
logger      = logging.getLogger('cnSpider')
hdlr        = logging.FileHandler(get_project_settings().get('LOGPATH')+"/cn/"+datetime.datetime.now().strftime("%Y%m%d")+".log")
formatter   = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 

class CnBookSpider(CrawlSpider):
    name            = "cn_book_spider"
#    start_urls      = []
   
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES':{
            'scrapyjs.SplashMiddleware': 725,
        },
        'ITEM_PIPELINES': {
            'findbook.pipelines.CnBookCrawlerPipeline': 400
        }
    }
    
    def __init__(self):
        logging.info('begin cnBook crwaler')
        self.settings       = get_project_settings()
        self.FoundBooks     = []
        self.notFoundBooks  = []
        self.settings       = get_project_settings()
        self.proxy_list     = self.settings.get('PROXY_LIST')
        self.proxies        = {}
        self.filePath       = self.settings.get('FILEPATH')
        self.fileName       = self.filePath+'/cn/'+datetime.datetime.now().strftime("%Y%m%d")+'.xlsx'
        
        dispatcher.connect(self.spider_closed, signals.spider_closed)


    def start_requests(self):
        logger.info('begin request')
        searchUrl       = 'http://search.dangdang.com/?key='
        fileNm          = self.settings.get('RECORDPATH')+"/cn/"+datetime.datetime.now().strftime("%Y%m%d")+".txt"
#        print(fileNm)
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
        url     = response.xpath('//ul[@class="bigimg"]/li/a[@class="pic"]/@href').extract_first()
#        return [scrapy.FormRequest(urls.extract_first(), 
#                                   callback=self.parse)] 
        self.logger.info('crawl product url:'+ url)
        if url is not None:
            yield scrapy.Request(url=url, callback=self.parse, errback=self.errback, meta={
                   'splash': {
                        'args': {
                            'wait':5,
#                            'proxy': random.choice(list(self.proxies.keys()))  
                            },
                        'endpoint':'render.html'
                        },
                    'isbn': isbn
                   }) 
        else:
            self.notFoundBooks.append(isbn)
    
    def errback(self, failure):
        self.logger.info('request failed')
        response = failure.value.response
        self.logger.error(response)
        isbn = failure.request.meta['isbn']
        self.notFoundBooks.append(isbn)
        
    def parse(self, response):
#        print(response.request.meta)
        price       = []
        price_text  = response.xpath('//div[@id="original-price"]/text()')
        price_text.extract()
        pattern     = re.compile("<[^<>]+>")
        for index, text in enumerate(price_text):
            price.append(text.extract().replace(' ', '').rstrip().replace('\r\n', ''))
        price       = ''.join(price)
        title       = response.xpath('//div[@class="name_info"]/h1/@title').extract_first()

        if price is not None and title is not None:
            tag     = []   
            tags    = response.xpath('//li[@id="detail-category-path"]/span/a/text()')
            tags.extract()
            for index, tag_item in enumerate(tags):
                tag.append(tag_item.extract())
            tag                 = ' '.join(tag)
            book                = CnBook()
            book['url']         = response.url
                                               
            book['picture']     = response.xpath('//img[@id="largePic"]/@src').extract_first()
            book['title_main']  = title
            
            book['publisher']   = response.xpath('//span[@dd_name="出版社"]/a/text()').extract_first()
            book['author']      = response.xpath('//span[@id="author"]/a/text()').extract_first()
            isbn                = response.xpath('//div[@id="detail_describe"]/ul/li/text()')[8].re_first(r'国际标准书号ISBN：\s*(.*)')
            
            book['isbn']        = isbn
            
            self.FoundBooks.append(isbn);
            
            book['sale_date']   = response.xpath('//div[@id="detail_describe"]/ul/li/text()')[3].re_first(r'印刷时间：\s*(.*)')

            
            book['price_cny']   = price
            book['price_twd']   = (int(float(price)) * 5)
            
            book['type']        = tag
#                print(str(response.xpath('//div[@id="detail"]').extract_first()))
            
            book['content']     = pattern.sub("", str(response.xpath('//div[@id="content"]/div[@class="descrip"]').extract_first()))
            yield book  
    
    def spider_closed(self, spider):
        logger.info('spider closed')
        logger.info('book found length:'+str(len(self.FoundBooks)))
        logger.info('book not found length:'+str(len(self.notFoundBooks)))
        