import scrapy
import logging
from ..items import BookParserItem


class BooksSpider(scrapy.Spider):

    logging.basicConfig(
        filename='log.txt',
        format='%(levelname)s: %(message)s',
        level=logging.ERROR
    )

    name = 'books'
    allowed_domains = [
        'books.toscrape.com',
    ]
    start_urls = [
        'http://books.toscrape.com/'
    ]

    def parse(self, response):
        links = response.css("article.product_pod > h3 > a ::attr(href)").extract()

        for link in links:
            yield scrapy.Request(
                response.urljoin(link),
                callback=self.parse_books
            )
        next_link = response.css("li.next > a ::attr(href)").extract_first()
        if next_link is not None:
            yield scrapy.Request(response.urljoin(next_link), callback=self.parse)

    def parse_books(self, response):
        block = response.css('.product_main')
        item = BookParserItem()
        item['genre'] = self.parse_genre(block)
        item['title'] = self.parse_title(block)
        description = self.parse_description(block)
        if not description:
            description = "0"
        item['description'] = description
        item['price'] = self.parse_price(block)
        item['rating'] = ''.join(self.parse_rating(block)).replace('star-rating ', '')
        product_information = self.parse_product_information(block)
        item['upc'] = product_information[0]
        item['product_type'] = product_information[1]
        item['price_excl_tax'] = product_information[2]
        item['price_incl_tax'] = product_information[3]
        item['tax'] = product_information[4]
        item['availability'] = product_information[5]
        item['num_reviews'] = product_information[6]
        item['images'] = 'http://books.toscrape.com/' + self.parse_image(block).replace('../../', '')
        item['image_urls'] = [item['images']]
        yield item

    def parse_genre(self, response):
        return response.xpath(
            '//ul[@class="breadcrumb"]'
            '/li[@class="active"]'
            '/preceding-sibling::li[1]'
            '/a'
            '/text()'
         ).extract_first()

    def parse_title(self, response):
        return response.css('h1::text').extract_first()

    def parse_image(self, response):
        return response.xpath(
                '//img/@src'
            ).extract_first()

    def parse_price(self, response):
        return response.css('p.price_color::text').extract_first().strip()

    def parse_rating(self, response):
        return response.xpath('//p[3]/@class').extract()

    def parse_description(self, response):
        return  response.xpath(
                '//div[@id="product_description"]'
                '/following-sibling::p'                
                '/text()'
            ).extract_first()

    def parse_product_information(self, response):
        return response.xpath(
            '//table[@class="table table-striped"]'
            '//td' 
            '/text()[1]'
        ).extract()


