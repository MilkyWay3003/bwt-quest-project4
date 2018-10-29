# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class BookParserItem(Item):
    genre = Field()
    title = Field()
    price = Field()
    rating = Field()
    description = Field()
    upc = Field()
    product_type = Field()
    price_excl_tax = Field()
    price_incl_tax = Field()
    tax = Field()
    availability = Field()
    num_reviews = Field()
    image_urls = Field()
    images = Field()



