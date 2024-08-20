import scrapy
import json
from scrapy.crawler import CrawlerProcess

class ScrapSpider(scrapy.Spider):
    name = "whisky"
    start_urls = ['https://nobero.com/collections/men-oversized-t-shirts?page=1']
    base_url = 'https://nobero.com/collections/men-oversized-t-shirts'
    
    def parse(self, response):
        product_links = response.css('a.product_link')
        
        if not product_links:
            return

        for link in product_links:
            full_link = response.urljoin(link.attrib['href'])
            yield scrapy.Request(full_link, callback=self.parse_detail)

        # Get the current page number from the URL
        current_page = int(response.url.split('=')[-1])

        # Construct the URL of the next page
        next_page = f'{self.base_url}?page={current_page + 1}'

        # Yield a request to the next page
        yield scrapy.Request(next_page, self.parse)

    def parse_detail(self, response):
        tit = response.css('h1.capitalize::text').get()
        price_text = response.css('h2#variant-price spanclass::text').get()
        mrp_text = response.css('span#variant-compare-at-price spanclass::text').get()
        last_sale = response.css('.product_bought_count span::text').get()

        script_content = response.css('script.product-json::text').get()
        variants_data = json.loads(script_content)

        attributes = {}
        for metafield in response.css('div.product-metafields-values'):
            key = metafield.css('h4::text').get().strip()
            value = metafield.css('p::text').get().strip()
            attributes[key] = value

        colors = {}
        for variant in variants_data:
            color = variant['option1']
            size = variant['option2']
            available = variant['available']

            if color not in colors:
                colors[color] = {'sizes': set(), 'available': False}
            
            if available:
                colors[color]['available'] = True
                colors[color]['sizes'].add(size)

        color_sizes = []
        for color, data in colors.items():
            color_sizes.append({
                'color': color,
                'size': list(data['sizes']) if data['available'] else []
            })

        description = []
        for item in response.css('#description_content p'):
            strong_texts = item.css('strong::text').getall()
            span_texts = item.css('span::text').getall()

            for strong, span in zip(strong_texts, span_texts):
                description.append(f"{strong.strip()}: {span.strip()}")

            for remaining_span in span_texts[len(strong_texts):]:
                description.append(remaining_span.strip())

        yield {
            "title" : tit.strip() if tit else 'NA',
            "price" : price_text.strip('₹') if price_text else 'NA',
            "product_urls": response.url,
            "MRP"   : mrp_text.strip('₹') if mrp_text else 'NA',
            "last_7_day_sale" : last_sale.strip().split()[0] if last_sale else 'NA',
            "available_skus": color_sizes,
            "fit": attributes.get('Fit', 'NA'),
            "fabric": attributes.get('Fabric', 'NA'),
            "neck": attributes.get('Neck', 'NA'),
            "sleeve": attributes.get('Sleeve', 'NA'),
            "pattern": attributes.get('Pattern', 'NA'),
            "length": attributes.get('Length', 'NA'),
            "description": ' / '.join(description)
        }

# Set up the crawler process
process = CrawlerProcess(settings={
    "FEEDS": {
        "output.json": {"format": "json"},
    },
})

# Run the spider
process.crawl(ScrapSpider)
process.start()