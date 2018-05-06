# ISBN找書

利用ISBN碼去簡體、英文、日文書網站爬書籍資料

## 準備

此專案是使用python作為開發，請按照以下步驟來安裝此專案必需的相關工具

### 專案前置作業

1. 安裝python IDE，此例是用windows作為開發所以請至https://www.anaconda.com/download/ 下載開發工具

2. 下載安裝至電腦後，請利用PyPI cmd安裝本專案所使用的framework：scrapy

```
pip install Scrapy
```

3.  此專案需要安裝額外兩個pakages：scrapy_proxies和scrapy-splash

```
pip install scrapy_proxies
```

```
pip install scrapy-splash
```

4.  此專案將會使用到splash service，在此例是用windows作為部屬環境所以請先安裝docker，https://docs.docker.com/docker-for-windows/
，安裝完後再用docker抓下splash的映像檔

```
sudo docker pull scrapinghub/splash
```

### 安裝專案

請將整包專案下載至你開發用的資料夾底下

## 執行專案

1.  在書籍語言對應的資料夾內(例：data/txt/cn)新增你需要爬資料的書籍ISBN，檔名為YYYYMMDD.txt，每個ISBN間用斷行隔開

2. 使用docker執行splash service

```
sudo docker run -p 8050:8050 -p 5023:5023 scrapinghub/splash
```

3. 在crawl_process.py所在的資料夾層，啟動專案

```
python crawl_process.py
```

4. ISBN有爬成功的書籍資料會寫入在data/xlsx/語言對應的資料夾內，圖片則是會下載至data/img/語言對應的資料夾內

## 專案相關工具

* [Anaconda](https://www.anaconda.com/download/) - python 開發用的IDE
* [Scrapy](https://doc.scrapy.org/en/latest/intro/tutorial.html) - 爬蟲使用的framework
* [docker](https://docs.docker.com/docker-for-windows/) - splash service使用的container 工具
* [splash](https://splash.readthedocs.io/en/stable/) - javascript web 瀏覽器

