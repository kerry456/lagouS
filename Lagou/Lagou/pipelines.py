# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
from Lagou.items import LagouItem

class LagouPipeline(object):
    def process_item(self, item, spider):
        return item

class LagouMysqlPipeline(object):
    # def process_item(self, item, spider):
    def open_spider(self, spider):
        self.con=pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='123456', db='my_home',
                                 use_unicode=True, charset='utf8')
        self.cursor=self.con.cursor()

    def process_item(self, item, spider):
        if isinstance(item, LagouItem):
            # insert_sql='''INSERT INTO area(TITLE, AREA, PRICE, RENT_METHOD, ADDRESS, URL) VALUES ('{}', '{}', '{}', '{}', '{}', '{}','{}','{}','{}','{}')'''.format(
            #     item['date'], item['city'], item['AQI'], item['level'], item['PM2_5'], item['PM10'],item['SO2'],item['CO'],item['NO2'],item['O3'])
        # else:
            try:
                insert_sql = '''INSERT INTO lagou(ITEM_KEY,POSITIONNAME,WORKYEAR,EDUCATION,JOBNATURE,CREATETIME,SALARY,CITY,FINANCESTAGE,INDUSTRYFIELD,COMPANYFULLNAME,DISTRICT,POSITIONADVANTAGE) VALUES ('{}', '{}', '{}','{}', '{}', '{}','{}','{}','{}','{}','{}','{}','{}')'''.format(item['item_key'], item['positionName'], item['workYear'], item['education'], item['jobNature'], item['createTime'], item['salary'],item['city'],item['financeStage'], item['industryField'],item['companyFullName'],item['district'],item['positionAdvantage'])
                self.cursor.execute(insert_sql)  # 执行sql语句
                self.con.commit()  # 提交到数据库，insert和updata语句必须执行这句
            except Exception as e:
                print(e)
            return item

    def close_spider(self, spider):
        self.con.close()
