import scrapy
from typing import Generator, Dict
from scrapy.http.response import Response

def parse_size_data(sizes):
    data = {}
    for size in sizes:
        size_data = {}
        size_data['data-id'] = size.css('::attr(data-id)').get()
        size_data['data-dc-stock'] = size.css('::attr(data-dc-stock)').get()
        size_data['data-store-stock'] = size.css('::attr(data-store-stock)').get()
        size_data['data-variation-id'] = size.css('::attr(data-variation-id)').get()
        size_data['data-stock'] = size.css('::attr(data-stock)').get()
        data[size_data['data-variation-id']] = size_data
    return data

class GooutdoorsSpider(scrapy.Spider):
    name = "gooutdoors"

    def start_requests(self):
        yield scrapy.Request(
            url = 'https://www.gooutdoors.co.uk/sitemap'
        )

    def parse(self, response):
        for link in response.css('table.template_sitemap a::attr(href)').getall():
            yield response.follow(link, callback=self.parse_category)

    def parse_category(self, response: Response) -> Generator:
        for product in response.css('article.product-item'):
            data_package = {
                'product_id': product.css('::attr(data-pid)').get(),
                'category': {
                    'category_url': response.url,
                    'category_h1': response.xpath('//h1//text()').extract_first(),
                    'category_description': response.css('div.category-header-text p::text').get(),
                    'category_breadcrumb': response.css('div#breadcrumb a::attr(href)').getall(),
                    'category_meta': {
                        'category_meta_title': response.xpath("//title/text()").extract_first(),
                        'category_meta_description': response.xpath("//meta[@name='description']/@content").extract_first(),
                        'category_meta_keywords': response.xpath("//meta[@name='keywords']/@content").extract_first(),
                    },
                    'category_misc': {
                        'category_filters': response.css('ul.template_nav_category li a span.cat-name::text').getall(),
                    }
                }
            }
            yield scrapy.Request(
                url = response.urljoin(product.css('a::attr(href)').get()),
                cb_kwargs = {'data_package': data_package}, 
                callback = self.parse_product
            )
        
        next_page = response.css('li.next-page a::attr(href)').get()
        if next_page is not None:
            yield response.follow(url = next_page)
    
    def parse_product(self, response: Response, data_package: Dict[str, str]) -> Generator:
        product_data = {
            'product_url': response.url,
            'product_brand': response.css('a.brand::text').get(),
            'product_name': response.css('span.product-name::text').get(),
            'product_retail_price': response.css('span.retail-price::text').get(),
            'product_current_price': response.css('span.regular-price::text').get(),
            'product_description': response.css('div.product-description ::text').get(),
            'product_specification': '\n'.join(response.css('div.product-details div.content-tab div.tab-content.current ::text').getall()),
            'product_images': response.css('a.image-thumb::attr(href)').getall(),
            'product_meta': {
                'product_meta_title': response.xpath("//title/text()").extract_first(),
                'product_meta_description': response.xpath("//meta[@name='description']/@content").extract_first(),
                'product_meta_keywords': response.xpath("//meta[@name='keywords']/@content").extract_first(),
            },
            'product_misc': parse_size_data(response.css('ul[rel="size"] li a'))
        }
        data_package['product'] = product_data
        yield data_package