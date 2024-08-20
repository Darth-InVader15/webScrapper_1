import scrapy
import json

class DetailSpider(scrapy.Spider):
    name = "data"
    start_urls = ['https://nobero.com/products/lunar-echo-oversized-t-shirt-1?variant=45663963218086']

    def parse(self,response):
        # details = response.css('main.flex.flex-col').get()
        tit = response.css('h1.capitalize::text').get()
        price_text = response.css('h2#variant-price spanclass::text').get()
        mrp_text = response.css('span#variant-compare-at-price spanclass::text').get()
        last_sale = response.css('.product_bought_count span::text').get()
          # Extract the JSON data from the script tag
        script_content = response.css('script.product-json::text').get()
        variants_data = json.loads(script_content)
        attributes = {}
        for metafield in response.css('div.product-metafields-values'):
            key = metafield.css('h4::text').get().strip()
            value = metafield.css('p::text').get().strip()
            attributes[key] = value
        

        yield attributes

        # Initialize dictionary to store colors and sizes
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

        for color, data in colors.items():
            yield {
                'color': color,
                'sizes': list(data['sizes']) if data['available'] else []
            }

        yield{
            "title" : tit.strip(),
            "price" : price_text.strip('₹'),
            "mrp"   : mrp_text.strip('₹'),
            "last_7day_sale" : last_sale.strip().split()[0] if last_sale else 'NA',


        }

        description = []

        # Loop through the <p> elements within #description_content
        for item in response.css('#description_content p'):
            # Extract the text from <strong> and <span> tags
            strong_texts = item.css('strong::text').getall()
            span_texts = item.css('span::text').getall()

            # Combine the <strong> and <span> texts
            for strong, span in zip(strong_texts, span_texts):
                description.append(f"{strong.strip()}: {span.strip()}")

            # Handle any remaining <span> tags not paired with a <strong>
            for remaining_span in span_texts[len(strong_texts):]:
                description.append(remaining_span.strip())

        # Create a dictionary with the key "Description" and the formatted description
        attribute = {
            "Description": ' / '.join(description)
        }

        yield attribute