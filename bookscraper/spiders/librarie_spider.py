import scrapy

from bookscraper.items import BookItem
from scrapy_splash import SplashRequest


def compute_common_xpath_expr(method, query, only_text):
    if only_text:
        return f"//b[{method}(text(),'{query}')]/ancestor::tr/td[position()=2]/text()"
    return f"//b[{method}(text(),'{query}')]/ancestor::tr/td[position()=2]"


class LibrarieSpider(scrapy.Spider):
    name = 'librarienet'

    def __init__(self, isbn='', *args, **kwargs):
        super(LibrarieSpider, self).__init__(*args, **kwargs)
        self.isbn = isbn

    def start_requests(self):
        url = 'https://www.librarie.net/cautare-rezultate.php?t=Sapiens. Scurta istorie a omenirii'

        yield SplashRequest(url=url, callback=self.parse, args={'forbidden_content_types': 'text/css,font/*',
                                                                'filters': 'easylist'})

    def parse(self, response):
        urls = response.css('div.product_grid_coperta a::attr(href)').getall()
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_book_info)

    def parse_book_info(self, response):
        book = BookItem()
        isbn = response.xpath(compute_common_xpath_expr('starts-with', 'ISBN', True)).get()

        if isbn is not None and self.isbn == isbn.strip():
            if len(response.xpath("//b[starts-with(text(),'Pret')]")) > 0:
                price = response.xpath(f"concat({compute_common_xpath_expr('starts-with', 'Pret', True)},'.'"
                                       f",{compute_common_xpath_expr('starts-with', 'Pret', False)}"
                                       f"/sup/small/text())").get().replace('lei', '').strip()
            else:
                price_xpath_expr = compute_common_xpath_expr('contains', 'promo', False) + "/b/span"
                price = response.xpath(f"concat({price_xpath_expr}/text(),'.'"
                                       f",{price_xpath_expr}/sup/small/text())").get().replace('lei', '').strip()

            book['offer'] = {
                'link': response.url,
                'provider': 'Librarie.net',
                'price': float(price),
                'hasStock': True if response.xpath("//td[starts-with(text(),'Disponibilitate')]/text()") is not None
                else False,
                'transportationCost': 15.99
            }
            yield book
