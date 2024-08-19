import scrapy

class ProductSpider(scrapy.Spider):
    name = "prods"
    start_urls = ['https://nobero.com/collections/men-oversized-t-shirts']

    def parse(self, response):
        for link in response.css('a.product_link'):
         # Check if link exists before accessing attrib
            if link:
                yield {
                'link': link.attrib['href']
                }
            # yield response.follow(link.get(), self.parse_product)

        # yield {
        #         'name': response.css("h1.capitalize.text-lg.md:text-[1.375rem].font-[familySemiBold].leading-none::text")
        #     }
    