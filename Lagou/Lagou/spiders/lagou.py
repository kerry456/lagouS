# -*- coding: utf-8 -*-
import scrapy
import hashlib
import json
from urllib.parse import quote
from Lagou.items import LagouItem
import redis
import re

def encrypt_pwd(pwd):
    """
        拉勾网进行密码加密
        g = 'veenike'
        c.password = md5(c.password)
        c.password = md5(g + c.password + g)
    :param pwd:
    :return:
    """
    import hashlib
    m = hashlib.md5()
    # 单独将密码进行 md5
    m.update(pwd.encode())
    # 得到密码加密后的 32 位 十六进制 md5 字符串
    a = m.hexdigest()
    # 加密密码的 盐
    g = 'veenike'
    # 这里必须获取一个新的md5对象！！！
    m1 = hashlib.md5()
    m1.update((g + a + g).encode())
    return m1.hexdigest()

class LagouSpider(scrapy.Spider):

    name = 'lagou'

    # 获取岗位信息时，需要提交这样的 cookie
    cookies = {
        'user_trace_token': '20180115085305-726d95a2-f98e-11e7-a34c-5254005c3644',
        'LGUID': '20180115085305-726d9864-f98e-11e7-a34c-5254005c3644'
    }

    def start_requests(self):
        """
            访问登录首页
        :return:
        """
        url = 'https://passport.lagou.com/login/login.html'
        yield scrapy.Request(url, callback=self.login, dont_filter=True)

    def get_item_keys(self):
        import redis
        r = redis.Redis(host=self.settings['REDIS_HOST'])
        item_keys = r.lrange('item_keys', 0, -1)
        return item_keys

    def login(self, response):
        """
            进行登录提交
        :param response:
        :return:
        """
        text = response.text
        # 在登录首页上，获取到需要补充到headers中的2个参数
        X_Anti_Forge_Token = re.search(r"window.X_Anti_Forge_Token.*?=.*?'(.*?)';", text).group(1)
        X_Anti_Forge_Code = re.search(r"window.X_Anti_Forge_Code.*?=.*?'(.*?)';", text).group(1)

        # 从配置文件中，获取 登录 的 用户名和密码
        user = self.settings['USER']
        pwd = self.settings['PWD']
        url = 'https://passport.lagou.com/login/login.json'
        data = {
            'isValidate': 'true',
            'username': user,
            'password': encrypt_pwd(pwd),
            'request_form_verifyCode': '',
            'submit': ''
        }

        # 创建登录提交的 post 方式的 request
        request = scrapy.FormRequest(url=url, formdata=data, callback=self.login_in, dont_filter=True)
        # 在 request 的headers中 增加2个必须的选项
        request.headers.setdefault('X-Anit-Forge-Code', X_Anti_Forge_Code)
        request.headers.setdefault('X-Anit-Forge-Token', X_Anti_Forge_Token)

        yield request

    def login_in(self, response):
        """
            登录成功后，进行岗位的搜索
        :param response:
        :return:
        """
        # 从配置文件中获取需要爬取的 岗位 列表
        item_keys = self.settings['ITEM_KEYS']
        # item_keys = self.get_item_keys()
        for key in item_keys:
            # key = key.decode()
            search_text_url = quote(key)
            url = f'https://www.lagou.com/jobs/list_{search_text_url}?labelWords=&fromSearch=true&suginput='
            # 创建 相应岗位的 搜索 请求
            yield scrapy.Request(url, callback=self.positionAjax, meta={'item_key': key},
                                 dont_filter=True)

    def positionAjax(self, response):
        """
            获取对应的 岗位列表
        :param response:
        :return:
        """
        referer_url = response.url
        search_text = response.meta['item_key']

        for i in range(1, 30):
            url = 'https://www.lagou.com/jobs/positionAjax.json?needAddtionalResult=false'
            data = {
                'first': 'false',
                'pn': str(i),
                'kd': search_text
            }
            # 创建 获取 岗位列表的 request ， post请求
            request = scrapy.FormRequest(url=url, formdata=data, callback=self.parse_item,
                                         meta={'item_key': search_text}, dont_filter=True,
                                         cookies=self.cookies)
            request.headers.setdefault('Referer', referer_url)

            yield request

    def parse_item(self, response):
        """
            已经正确获取到 岗位列表 的json返回，进行结构化处理
        :param response:
        :return:
        """
        text = response.text
        json_data = json.loads(text)
        results = json_data['content']['positionResult']['result']

        # 每页 15 个结果，进行遍历
        for result in results:

            # 数据结构化
            item = LagouItem()
            item['item_key'] = response.meta['item_key']

            item['positionName'] = result['positionName']
            item['workYear'] = result['workYear']
            item['education'] = result['education']
            item['jobNature'] = result['jobNature']
            item['createTime'] = result['createTime']
            item['salary'] = result['salary']
            item['city'] = result['city']
            item['financeStage'] = result['financeStage']
            item['industryField'] = result['industryField']
            item['companyFullName'] = result['companyFullName']
            item['district']  = result['district']
            item['positionAdvantage'] = result['positionAdvantage']
            #  提交 item 给 pipeline 进行处理
            yield item
