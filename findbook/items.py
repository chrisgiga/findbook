# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JpBook(scrapy.Item):
    # define the fields for your item here like:
     url        = scrapy.Field()
     title_main = scrapy.Field()
     author     = scrapy.Field()
     picture    = scrapy.Field()
     page       = scrapy.Field()
     isbn       = scrapy.Field()
     ean        = scrapy.Field()
     category   = scrapy.Field()
     type       = scrapy.Field()
     content    = scrapy.Field()
     price      = scrapy.Field()
     sale_date  = scrapy.Field()
     publisher  = scrapy.Field()
     price_twd  = scrapy.Field()

class BookImage(scrapy.Item):
    image_urls  = scrapy.Field()
    images      = scrapy.Field()
    image_name  = scrapy.Field()
    extension   = scrapy.Field()
    
class CnBook(scrapy.Item):
    # define the fields for your item here like:
     url        = scrapy.Field()
     title_main = scrapy.Field()
     author     = scrapy.Field()
     publisher  = scrapy.Field()
     picture    = scrapy.Field()
     isbn       = scrapy.Field()
     type       = scrapy.Field()
     content    = scrapy.Field()
     price_cny  = scrapy.Field()
     price_twd  = scrapy.Field()
     sale_date  = scrapy.Field()
     
class EnBook(scrapy.Item):
    # define the fields for your item here like:
     url        = scrapy.Field()
     title_main = scrapy.Field()
     author     = scrapy.Field()
     publisher  = scrapy.Field()
     picture    = scrapy.Field()
     isbn13     = scrapy.Field()
     category   = scrapy.Field()
     content    = scrapy.Field()
     price_org  = scrapy.Field()
     price_twd  = scrapy.Field()
     sale_date  = scrapy.Field()