# -*- coding: utf-8 -*-
"""
Created on Thu Feb  1 16:30:58 2018

@author: taaze
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
logger = logging.getLogger('cnImgSpider')
hdlr = logging.FileHandler(get_project_settings().get('LOGPATH')+"/cn/"+datetime.datetime.now().strftime("%Y%m%d")+".log")
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 

class CnBookImgSpider(CrawlSpider):
    name            = "cn_book_img_spider"
    start_urls      = []
    settings        = get_project_settings()
    filePath        = settings.get('IMGPATH')+"/cn/"+datetime.datetime.now().strftime("%Y%m%d")
    
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
        logger.info('begin cnBookImg crwaler')
        self.settings  = get_project_settings()
        self.filePath  = self.settings.get('IMGPATH')+"/cn/"+datetime.datetime.now().strftime("%Y%m%d")
        self.csvFile   = self.settings.get('FILEPATH')+"/cn/"+datetime.datetime.now().strftime("%Y%m%d")+".csv"
        self.zipFile   = self.settings.get('IMGPATH')+"/cn/"+datetime.datetime.now().strftime("%Y%m%d")+".zip"
        if not os.path.exists(self.filePath):
            os.makedirs(self.filePath)
        dispatcher.connect(self.spider_closed, signals.spider_closed)
        
    def start_requests(self):
        searchUrl       = 'http://search.dangdang.com/?key='
        fileNm          = self.settings.get('RECORDPATH')+"/cn/"+datetime.datetime.now().strftime("%Y%m%d")+".txt"
        fin             = open(fileNm)
        try:
            for line in fin.readlines():
                isbn = line.strip()
#                logger.info('isbn:'+isbn)
                yield scrapy.FormRequest(searchUrl+isbn, callback=self.parse_list, meta={'isbn': isbn})     
        finally:
            fin.close()      
            
    def parse_list(self, response):
        logger.info('begin parse list')
        isbn    = response.meta['isbn']
        urls    = response.xpath('//ul[@class="bigimg"]/li/a[@class="pic"]/@href')
        return [scrapy.FormRequest(urls.extract_first(), callback=self.parse, meta={'isbn': isbn })] 

    
    def parse(self, response):
        img                 = BookImage()
        isbn                = response.meta['isbn']
        img['image_name']   = isbn
#        response.xpath('//div[@id="detail_describe"]/ul/li/text()')[8].re_first(r'国际标准书号ISBN：\s*(.*)')
        img['image_urls']   = [response.xpath('//img[@id="largePic"]/@src').extract_first()]
        return img
    
    
    def spider_closed(self, spider):
        logger.info('spider closed')
        zf = zipfile.ZipFile(self.zipFile, mode='w')
        os.chdir(self.filePath)
        for root, folders, files in os.walk(".\\"):
            for sfile in files:
                aFile = os.path.join(root, sfile)
                zf.write(aFile)
        zf.close()
        os.chdir(self.settings.get('IMGPATH')+"/cn/")
        shutil.rmtree(self.filePath)
