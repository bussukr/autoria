# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from dataclasses import dataclass

@dataclass
class AutoriaItem:
    # define the fields for your item here like:
    # name = scrapy.Field()
    auto_id: int = 0
    product_link: str = ''
    product_name: str = ''
    brand: str = ''
    model: str = ''
    production_date: int = 0
    mileage: int = 0
    body_type: str = ''
    color: str = ''
    gearbox_type: str = ''
    price_currency: str = ''
    price: float = 0.0
    usd_exch_rate: float = 0.0 
    eur_exch_rate: float = 0.0
    description: str = ''
