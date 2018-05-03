# -*- coding: utf-8 -*-
"""
Created on Thu Nov 16 09:26:41 2017

@author: taaze
"""


import requests  
from bs4 import BeautifulSoup  
from multiprocessing import Process, Queue  
import random  
from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess


class Proxies(object):  
    def __init__(self, page=5):  
        self.proxies = []  
        self.verify_pro = []  
        self.page = page  
        self.headers = {  
        'Accept': '*/*',  
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36',  
        'Accept-Encoding': 'gzip, deflate, sdch',  
        'Accept-Language': 'zh-CN,zh;q=0.8'  
        }  
        self.get_proxies()  
#        self.get_proxies_nn()  
    
    def get_proxies(self):
        url = 'https://free-proxy-list.net/'  
        html = requests.get(url, headers=self.headers).content  
        soup = BeautifulSoup(html, 'lxml')  
        ip_list = soup.find(id='proxylisttable').find("tbody")  

        for odd in ip_list.find_all("tr"):  
            ssl = odd.find_all('td')[6].get_text().lower()
            if ssl == "yes":
                protocol = 'https://'  
            if ssl == "no":
                protocol = 'http://'  
            if protocol == "http://":
                self.proxies.append(protocol + ':'.join([x.get_text() for x in odd.find_all('td')[0:2]]))  
        
    def get_proxies_nn(self):

        page = random.randint(1,20)  

        page_stop = page + self.page  

        while page < page_stop:  
            url = 'http://www.xicidaili.com/nn/%d' % page  
            html = requests.get(url, headers=self.headers).content  
            soup = BeautifulSoup(html, 'lxml')  
            ip_list = soup.find(id='ip_list')  
            for odd in ip_list.find_all(class_='odd'):  
                protocol = odd.find_all('td')[5].get_text().lower() + '://'  
                if protocol == "http://":
                    self.proxies.append(protocol + ':'.join([x.get_text() for x in odd.find_all('td')[1:3]]))  
            page += 1  
            
    def verify_proxies(self):  
        # 没验证的代理  
        old_queue = Queue()  
        # 验证后的代理  
        new_queue = Queue()  
        print ('verify proxy........')  
        works = []  
        for _ in range(15):  
            works.append(Process(target=self.verify_one_proxy, args=(old_queue,new_queue)))  
        for work in works:  
            work.start()  
        for proxy in self.proxies:  
            old_queue.put(proxy)  
        for work in works:  
            old_queue.put(0)  
        for work in works:  
            work.join()  
        self.proxies = []  
        while 1:  
            try:  
                self.proxies.append(new_queue.get(timeout=1))  
            except:  
                break  
        print ('verify_proxies done!')  
        
    def verify_one_proxy(self, old_queue, new_queue):  
         while 1:  
            proxy = old_queue.get()  
            if proxy == 0:break  
            protocol = 'https' if 'https' in proxy else 'http'  
            proxies = {protocol: proxy}  

            try:  
                request = requests.get('http://www.dangdang.com/', proxies=proxies, timeout=2)
                if request.status_code == 200:  
                    print ('success %s' % proxy)  
                    new_queue.put(proxy)  
                else:
                    print(request.status_code)
            except:  
                print ('fail %s' % proxy)  
            
                
if __name__ == '__main__':  
    a = Proxies()  
    a.verify_proxies()  
    print (a.proxies)  
    proxie = a.proxies   
    with open('C:/python_app/findbook/proxies/list.txt', 'a') as f:  
       for proxy in proxie:  
             f.write(proxy+'\n')     
    
#    setting = get_project_settings()
#    process = CrawlerProcess(setting)
#    try: 
#        process.crawl('cn_book_spider')
#        process.crawl('cn_book_img_spider')
#        process.crawl('en_book_spider')
#        process.crawl('en_book_img_spider')
#        process.crawl('jp_book_spider')
#        process.crawl('jp_book_img_spider')
#        process.start()
#    except:
#        print ('fail to start process')  
