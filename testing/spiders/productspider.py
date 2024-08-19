import scrapy

class ProductSpider(scrapy.Spider):
    name = "prods"
    start_urls = ['https://nobero.com/collections/men-oversized-t-shirts?page=1']

    def parse(self, response):
        product_links = response.css('a.product_link')
        
        if not product_links:
            return

        for link in product_links:
            yield {
                'link': link.attrib['href']
            }

        # Get the current page number from the URL
        current_page = int(response.url.split('=')[-1])

        # Construct the URL of the next page
        next_page = f'https://nobero.com/collections/men-oversized-t-shirts?page={current_page + 1}'

        # Yield a request to the next page
        yield scrapy.Request(next_page, self.parse)