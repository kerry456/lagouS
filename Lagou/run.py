'''
auth:hexl
'''
from Lagou.spiders.lagou import LagouSpider
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# 获取settings.py模块的设置
settings = get_project_settings()
process = CrawlerProcess(settings=settings)

#添加spider
process.crawl(LagouSpider)
#启动spider
process.start()