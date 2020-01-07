import scrapy
class BlogSpider(scrapy.Spider):
    name = 'blogspider'
    start_urls = ['https://blog.scrapinghub.com']
    def parse(self, response):
	titles = response.css('.title.may-blank::text').extract()
	yield titles
