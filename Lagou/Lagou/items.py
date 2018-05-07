# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class LagouItem(scrapy.Item):
    # define the fields for your item here like:
    #搜索岗位关键字
    item_key = scrapy.Field()
    # 职位名
    positionName=scrapy.Field()
    # 工作年限
    workYear=scrapy.Field()
    # 教育经历
    education=scrapy.Field()
    # 职业类型
    jobNature=scrapy.Field()
    # 发布时间
    createTime=scrapy.Field()
    # 薪资
    salary=scrapy.Field()
    # 工作城市
    city=scrapy.Field()
    # 是否融资
    financeStage=scrapy.Field()
    # 公司类型
    industryField=scrapy.Field()
    # 公司名称
    companyFullName=scrapy.Field()
    # 公司地址
    district=scrapy.Field()
    # 公司福利
    positionAdvantage=scrapy.Field()

