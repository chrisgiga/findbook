# -*- coding: utf-8 -*-
"""
Created on Tue Feb  6 16:09:46 2018

@author: chris
"""

import os
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from findbook.items import BookImage
from scrapy.utils.project import get_project_settings
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
import datetime
import zipfile
import shutil
import logging
logger = logging.getLogger('enImgSpider')
hdlr = logging.FileHandler(get_project_settings().get('LOGPATH')+"/en/"+datetime.datetime.now().strftime("%Y%m%d")+".log")
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 

class EnBookImgSpider(CrawlSpider):
    name            = "en_book_img_spider"
    start_urls      = []
    settings        = get_project_settings()
    filePath        = settings.get('IMGPATH')+"/en/"+datetime.datetime.now().strftime("%Y%m%d")
    
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES':{
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': 90,
             'scrapy_proxies.RandomProxy': 100,
        },
        'ITEM_PIPELINES': {
            'findbook.pipelines.ImagesPipline':200
        },
        'IMAGES_STORE' : filePath
    }
    
    def __init__(self):
        logger.info('begin enBookImg crwaler')
        self.settings       = get_project_settings()
        self.filePath       = self.settings.get('IMGPATH')+"/en/"+datetime.datetime.now().strftime("%Y%m%d")
        self.csvFile        = self.settings.get('FILEPATH')+"/en/"+datetime.datetime.now().strftime("%Y%m%d")+".csv"
        self.zipFile        = self.settings.get('IMGPATH')+"/en/"+datetime.datetime.now().strftime("%Y%m%d")+".zip"
        if not os.path.exists(self.filePath):
            os.makedirs(self.filePath)
        dispatcher.connect(self.spider_closed, signals.spider_closed)
        
    def start_requests(self):
        logger.info('begin request')
        searchUrl       = 'https://www.bookdepository.com/search?searchTerm='
        fileNm          = self.settings.get('RECORDPATH')+"/en/"+datetime.datetime.now().strftime("%Y%m%d")+".txt"
#        print(fileNm)
        fin = open(fileNm)
        try:
            for line in fin.readlines():
                isbn = line.strip()
#                print(isbn)
                yield scrapy.Request(url=searchUrl+isbn, callback=self.parse, meta={'isbn':isbn})      
        finally:
            fin.close()     
        
    def parse(self, response):
        img = BookImage()
        img['image_name'] = response.xpath('//ul[@class="biblio-info"]/li/span[@itemprop="isbn"]/text()').extract_first()
        img['image_urls'] = [response.xpath('//div[@class="item-img-content"]/img/@src').extract_first()]
        return img
    
    def spider_closed(self, spider):
        logger.info('spider closed')
        zf = zipfile.ZipFile(self.zipFile, mode='w')
        os.chdir(self.filePath)
        for root, folders, files in os.walk(".\\"):
            for sfile in files:
                aFile = os.path.join(root, sfile)
                #print aFile
                zf.write(aFile)
        zf.close()
        os.chdir(self.settings.get('IMGPATH')+"/en/")
        shutil.rmtree(self.filePath)
        