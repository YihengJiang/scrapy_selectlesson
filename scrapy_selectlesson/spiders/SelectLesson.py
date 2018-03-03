#!/usr/bin/env python
# -*- coding:utf-8 -*-

import copy
import scrapy
from scrapy.http.cookies import CookieJar
import math
import time

cookie = CookieJar()
cookieDict = {}
login_url = 'https://passport.ustc.edu.cn/login?service=http%3A%2F%2Fyjs%2Eustc%2Eedu%2Ecn%2Fdefault%2Easp'
userInfo = {}
post_headers = {
    #     'Accept': 'text/html, application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    #     'Accept-Encoding':'gzip,deflate,br',
    #     'Accept-Language':'zh-CN,zh;q=0.9',
    #     'Cache-Control':'max-age=0',
    #     'Connection':'keep-alive',
    #     'Content-Length':'113',
    #     'Content-Type':'application/x-www-form-urlencoded',
    #     'Cookie':'laravel_session='+cookieDict['laravel_session'],
    #     'Host':'passport.ustc.edu.cn',
    #     'Origin':'https://passport.ustc.edu.cn',
    #     'Referer':'https://passport.ustc.edu.cn/login?service=http%3A%2F%2Fyjs%2Eustc%2Eedu%2Ecn%2Fdefault%2Easp',
    #     'Upgrade-Insecure-Requests':'1',
    #     'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, likeGecko) Chrome/64.0.3282.186 Safari/537.36'

    #     "Proxy-Connection": "keep-alive",
    #     "Pragma": "max-age=0",
    # "Cache-Control": "no-cache",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36",
    # " Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0",
    "Accept": "*/*",  # "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    # "DNT": "1",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-US,en;q=0.5",  # "zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4",
    # "Accept-Charset": "gb2312,gbk;q=0.7,utf-8;q=0.7,*;q=0.7",
    "Connection": "keep-alive",
    # "Host":"mis.teach.ustc.edu.cn",
    # # "If-Modified-Since":"0", # spider do not need this value
    # "Referer":"http://mis.teach.ustc.edu.cn/gradGetDxkc.do",
    # "Upgrade-Insecure-Requests":"1",
}


class SelectLessonSpider(scrapy.Spider):
    name = 'sel'

    def __init__(self, info, *args, **kwargs):
        super(SelectLessonSpider, self).__init__(*args, **kwargs)
        inf = str(info).split("_")
        userInfo['name'] = inf[0]
        userInfo['password'] = inf[1]
        self.interval=inf[2]
        userInfo['lessonId'] = inf[3:]

    def start_requests(self):
        urls = [login_url, ]
        # must return an iterable data structure,like generator or list and so on.
        header = copy.deepcopy(post_headers)
        header["Referer"] = "http://yjs.ustc.edu.cn/DEFAULT.ASP"
        header["Host"] = "passport.ustc.edu.cn"
        header["Upgrade-Insecure-Requests"] = "1"

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse, headers=header)

    def parse(self, response):

        cookie.extract_cookies(response, response.request)
        for c in cookie:
            cookieDict[c.name] = c.value
        _token = response.xpath('//form/input/@value').extract()[0]

        header = copy.deepcopy(post_headers)
        header[
            "Referer"] = "https://passport.ustc.edu.cn/login?service=http%3A%2F%2Fyjs%2Eustc%2Eedu%2Ecn%2Fdefault%2Easp"
        header["Host"] = "passport.ustc.edu.cn"
        header["Upgrade-Insecure-Requests"] = "1"
        header["Origin"] = "https://passport.ustc.edu.cn"
        yield scrapy.FormRequest(
            url=login_url,
            # method='POST',
            formdata={'_token': _token, 'login': userInfo['name'], 'password': userInfo['password'], 'button': '登录'},
            callback=self.check_login,
            cookies=cookieDict,
            # dont_filter=True,
            # headers=post_headers
        )

    def check_login(self, response):
        if response.status == 302:
            cookie.extract_cookies(response, response.request)
            for c in cookie:
                cookieDict[c.name] = c.value
            redirect_url = response.xpath("//a[@href]/text()").extract()[0]
            header = copy.deepcopy(post_headers)
            header["Host"] = "yjs.ustc.edu.cn"
            header["Upgrade-Insecure-Requests"] = "1"
            yield scrapy.Request(url=redirect_url, callback=self.redirect_proc, headers=header)

    def redirect_proc(self, response):
        if response.status == 302:
            cookie.extract_cookies(response, response.request)
            for c in cookie:
                cookieDict[c.name] = c.value
            header = copy.deepcopy(post_headers)
            header["Host"] = "yjs.ustc.edu.cn"
            header["Upgrade-Insecure-Requests"] = "1"
            # yield scrapy.Request('http://mis.teach.ustc.edu.cn/gradLogin.do?stn='+userInfo['name']+'&ASPSESSIONIDCQBDAQCB='+cookieDict['ASPSESSIONIDCQBDAQCB'],self.preparSec,)
            url = 'http://yjs.ustc.edu.cn/main.asp'
            cookieKey = [i for i in cookieDict.keys() if i[:12] == 'ASPSESSIONID'][0]
            yield scrapy.Request(url, self.mainPage, headers=header, cookies={cookieKey: cookieDict[cookieKey]})

    def mainPage(self, response):
        if response.status == 200:
            cookie.extract_cookies(response, response.request)
            for c in cookie:
                cookieDict[c.name] = c.value
            header = copy.deepcopy(post_headers)
            header["Referer"] = "http://yjs.ustc.edu.cn/m_left.asp?area=5&menu=1"
            header["Host"] = "mis.teach.ustc.edu.cn"
            # header["If-Modified-Since"]="0"
            # header["Upgrade-Insecure-Requests"] = "1"
            cookieKey = [i for i in cookieDict.keys() if i[:12] == 'ASPSESSIONID'][0]
            sel_url = 'http://mis.teach.ustc.edu.cn/gradLogin.do?stn=' + userInfo['name'] + '&' + cookieKey + '=' + \
                      cookieDict[cookieKey]
            yield scrapy.Request(sel_url, self.openSelLesPage, headers=header)

    def openSelLesPage(self, response):
        # if response.status == 200:
        #     cookie.extract_cookies(response, response.request)
        #     for c in cookie:
        #         cookieDict[c.name] = c.value
        #
        #     header = copy.deepcopy(post_headers)
        #     # header["Referer"] = "http://mis.teach.ustc.edu.cn/gradInitXk.do"
        #     header["Host"] = "mis.teach.ustc.edu.cn"
        #     # http://mis.teach.ustc.edu.cn/gradGetDxkc.do
        #     # header["Upgrade-Insecure-Requests"] = "1"
        #     sel_url = 'http://mis.teach.ustc.edu.cn/gradInitXk.do'
        #     yield scrapy.Request(sel_url,self.initPage,headers=header,cookies={'JSESSIONID':cookieDict['JSESSIONID']})

        # header = copy.deepcopy(post_headers)
        # header["Referer"] = "http://mis.teach.ustc.edu.cn/gradInitXk.do"
        # header["Host"] = "mis.teach.ustc.edu.cn"
        # # http://mis.teach.ustc.edu.cn/gradGetDxkc.do
        # # header["Upgrade-Insecure-Requests"] = "1"
        # sel_url = 'http://mis.teach.ustc.edu.cn/gradGetDxkc.do'
        # yield scrapy.Request(sel_url,self.selRlt,headers=header,cookies={'JSESSIONID':cookieDict['JSESSIONID']})

        # if response.status == 200:
        #     cookie.extract_cookies(response, response.request)
        #     for c in cookie:
        #         cookieDict[c.name] = c.value
        #     header = copy.deepcopy(post_headers)
        #     header["Referer"] = "http://mis.teach.ustc.edu.cn/gradGetDxkc.do"
        #     header["Host"] = "mis.teach.ustc.edu.cn"
        #     header["If-Modified-Since"]="0"
        #     # header["Upgrade-Insecure-Requests"] = "1"
        #     sel_url = 'http://mis.teach.ustc.edu.cn/gradSaveKc.do?kcbjh=' + userInfo['lessonId']
        #     yield scrapy.Request(sel_url,self.initPage2,headers=header,cookies={'JSESSIONID':cookieDict['JSESSIONID']})
        if response.status == 200:
            cookie.extract_cookies(response, response.request)
            for c in cookie:
                cookieDict[c.name] = c.value
            header = copy.deepcopy(post_headers)
            # header["Referer"] = "http://mis.teach.ustc.edu.cn/gradGetDxkc.do"
            header["Host"] = "mis.teach.ustc.edu.cn"
            # header["If-Modified-Since"]="0"
            # header["Upgrade-Insecure-Requests"] = "1"
            sel_url = 'http://mis.teach.ustc.edu.cn/gradLoginSuc.do'
            yield scrapy.Request(sel_url, self.initPage2, headers=header,
                                 cookies={'JSESSIONID': cookieDict['JSESSIONID']})

    #
    # def initPage(self,response):
    #     header = copy.deepcopy(post_headers)
    #     header["Referer"] = "http://mis.teach.ustc.edu.cn/gradInitXk.do"
    #     header["Host"] = "mis.teach.ustc.edu.cn"
    #     header["Cookie"] = "JSESSIONID"+cookieDict['JSESSIONID']
    #     # http://mis.teach.ustc.edu.cn/gradGetDxkc.do
    #     # header["Upgrade-Insecure-Requests"] = "1"
    #     sel_url = 'http://mis.teach.ustc.edu.cn/gradGetDxkc.do'
    #
    #
    #     # yield scrapy.Request(sel_url,self.initPage2,headers=header,cookies={'JSESSIONID':cookieDict['JSESSIONID']})

    def initPage2(self, response):
        if response.status == 200:
            cookie.extract_cookies(response, response.request)
            for c in cookie:
                cookieDict[c.name] = c.value
            header = copy.deepcopy(post_headers)
            # header["Referer"] = "http://mis.teach.ustc.edu.cn/gradLoginSuc.do"
            header["Host"] = "mis.teach.ustc.edu.cn"
            # header["If-Modified-Since"]="0"
            # header["Upgrade-Insecure-Requests"] = "1"
            sel_url = 'http://mis.teach.ustc.edu.cn/gradInitXk.do'
            yield scrapy.Request(sel_url, self.initPage3, headers=header,
                                 cookies={'JSESSIONID': cookieDict['JSESSIONID']})

    def initPage3(self, response):
        if response.status == 200:
            cookie.extract_cookies(response, response.request)
            for c in cookie:
                cookieDict[c.name] = c.value
            header = copy.deepcopy(post_headers)
            header["Referer"] = "http://mis.teach.ustc.edu.cn/gradInitXk.do"
            header["Host"] = "mis.teach.ustc.edu.cn"
            # header["If-Modified-Since"]="0"
            # header["Upgrade-Insecure-Requests"] = "1"
            urls = ['http://mis.teach.ustc.edu.cn/gradGetDxkc.do', 'http://mis.teach.ustc.edu.cn/gradGetYxkc.do']
            for url in urls:
                yield scrapy.Request(url, self.initPage4, headers=header,
                                     cookies={'JSESSIONID': cookieDict['JSESSIONID']},dont_filter=True)

    def initPage4(self, response):
        if response.status == 200 and response.url == 'http://mis.teach.ustc.edu.cn/gradGetYxkc.do':

            print("============================== origin lessons ==============================\n")
            print("编号     名称      教师      单位      时间地点       学分      人数     起止周     类型\n")
            document_list = response.xpath("//div/table/*/td")
            item_str = ""
            for i in range(len(document_list)):
                modVa = math.fmod(i, 12)
                if modVa in [1, 3, 4, 6, 7, 8, 9]:
                    item_str += document_list[i].xpath("./text()").extract()[0]+" "
                elif modVa == 2:
                    item_str += document_list[i].xpath("./a/text()").extract()[0]+" "
                elif modVa == 5:
                    temp = document_list[i].xpath("./text()").extract()
                    temp=("|").join(temp)
                    item_str += temp+" "
                elif modVa==0:
                    print(item_str+"\n")
                    item_str=""
            print(item_str + "\n")

            header = copy.deepcopy(post_headers)
            header["Referer"] = "http://mis.teach.ustc.edu.cn/gradGetDxkc.do"
            header["Host"] = "mis.teach.ustc.edu.cn"
            header["If-Modified-Since"] = "0"
            # header["Upgrade-Insecure-Requests"] = "1"
            for lessonId in userInfo['lessonId']:
                yield scrapy.Request('http://mis.teach.ustc.edu.cn/gradSaveKc.do?kcbjh='+lessonId, self.selRlt, headers=header, cookies={'JSESSIONID': cookieDict['JSESSIONID']},dont_filter=True,meta={"count":0,"lessonId":lessonId})


    def selRlt(self, response):
        if response.status == 200:
            if response.text=="11":
                print("选课成功!!!\n")
                header = copy.deepcopy(post_headers)
                header["Referer"] = response.url
                header["Host"] = "mis.teach.ustc.edu.cn"
                # header["If-Modified-Since"]="0"
                # header["Upgrade-Insecure-Requests"] = "1"
                url = 'http://mis.teach.ustc.edu.cn/gradGetYxkc.do'
                yield scrapy.Request(url, self.initPage4, headers=header,
                                     cookies={'JSESSIONID': cookieDict['JSESSIONID']}, dont_filter=True)

            elif response.text=="12":
                print("选课成功 ,请在抽签结束后查看抽签结果！\n")
            elif response.text=="4":
                co=response.meta["count"]+1
                lessonId=response.meta["lessonId"]
                print("课堂已满员,将继续选择......|课程:"+lessonId+" | 选课次数:"+str(co)+"\n")
                time.sleep(int(self.interval)/1000)
                header = copy.deepcopy(post_headers)
                header["Referer"] = "http://mis.teach.ustc.edu.cn/gradGetDxkc.do"
                header["Host"] = "mis.teach.ustc.edu.cn"
                header["If-Modified-Since"] = "0"
                # header["Upgrade-Insecure-Requests"] = "1"

                yield scrapy.Request(response.url, self.selRlt, headers=header,
                                     cookies={'JSESSIONID': cookieDict['JSESSIONID']},dont_filter=True,meta={"count":co,"lessonId":lessonId})

            else:
                print("其他错误,程序终止!\n")
