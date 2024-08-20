import scrapy

class TitleSpider(scrapy.Spider):
    name = "tits"
    start_urls = ['https://nobero.com/products/mountain-adventure-oversized-t-shirt?variant=45724187852966']

    def parse(self, response):
        product = response.css('h1.capitalize::text').get()

        if product:
            yield{
                'text' : product.strip()
            }