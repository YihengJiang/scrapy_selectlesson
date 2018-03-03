#!/usr/bin/env python
# -*- coding:utf-8 -*-

import scrapy


class QuotesSpider(scrapy.Spider):
    name = 'quotes'

    # if we have urls ,we neednt overwrite start_requests()
    start_urls = [
        'http://quotes.toscrape.com/page/1/',
        'http://quotes.toscrape.com/page/2/'
    ]

    # def start_requests(self):
    #     urls = [
    #         'http://quotes.toscrape.com/page/1/',
    #         'http://quotes.toscrape.com/page/2/'
    #     ]
    #     # must return an iterable data structure,like generator or list and so on.
    #     for url in urls:
    #         yield scrapy.Requesturl= url, callback=self.parse)

    # def parse(self, response):
    # page = response.url.split('/')[-2]
    # fileName = 'quotes-%s.html' % page
    # with open(fileName, 'wb') as f:
    #     f.write(response.body)
    # self.log('saved file %s ' % fileName)

    def parse(self, response):
        for quote in response.xpath('//div[@class="quote"]'):
            yield {
                'text': quote.xpath('span[@class="text"]/text()').extract_first(),
                'author': quote.xpath('span/small[@class="author"]/text()').extract_first(),
                'tags': quote.xpath('div/a[@class="tag"]/text()').extract()}

            # iterate to crawl the inner page contents
            next_page = response.xpath('//li[@class="next"]/a/@href').extract_first()
            if next_page is not None:
                next_page = response.urljoin(next_page)
                yield scrapy.Request(url=next_page, callback=self.parse)
