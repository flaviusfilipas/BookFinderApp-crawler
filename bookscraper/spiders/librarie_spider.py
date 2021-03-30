import scrapy

from bookscraper.items import BookItem
from scrapy_splash import SplashRequest


def compute_common_xpath_expr(method, query, only_text):
    if only_text:
        return f"//b[{method}(text(),'{query}')]/ancestor::tr/td[position()=2]/text()"
    return f"//b[{method}(text(),'{query}')]/ancestor::tr/td[position()=2]"


class LibrarieSpider(scrapy.Spider):
    name = 'librarienet'

    def start_requests(self):
        url = 'https://www.librarie.net/cautare-rezultate.php?t=Sapiens. Scurta istorie a omenirii'

        yield SplashRequest(url=url, callback=self.parse, args={'forbidden_content_types': 'text/css,font/*',
                                                                'filters': 'easylist'})

    def parse(self, response):
        urls = response.css('div.product_grid_coperta a::attr(href)').getall()
        for url in urls:
            yield SplashRequest(url=url,
                                callback=self.parse_book_info,
                                meta={'link': url},
                                args={'wait': 1, 'forbidden_content_types': 'text/css,font/* ',
                                      'filters': 'easylist'})

    def parse_book_info(self, response):
        book = BookItem()
        book['author'] = response.xpath(compute_common_xpath_expr('starts-with', 'Autor(i)', False) + '/a/text()').get()
        book['title'] = response.css('div.css_titlu b::text').get()
        publisher = response.xpath(compute_common_xpath_expr('starts-with', 'Editura', False) + '/a/text()') \
            .get()
        number_of_pages = response.xpath(compute_common_xpath_expr('starts-with', 'Nr', True)).get()
        book['publisher'] = publisher.split()[1] if publisher is not None else None
        book['numberOfPages'] = number_of_pages.split()[0] if number_of_pages is not None else None
        cover_type = response.xpath(compute_common_xpath_expr('starts-with', 'Tip', True)).get()
        book['coverType'] = cover_type.strip().capitalize() if cover_type is not None else None
        book['isbn'] = response.xpath(compute_common_xpath_expr('starts-with', 'ISBN', True)).get()
        book['imgUrl'] = response.css('div.css_coperta img::attr(src)').get()
        if len(response.xpath("//b[starts-with(text(),'Pret')]")) > 0:
            price = response.xpath(f"concat({compute_common_xpath_expr('starts-with', 'Pret', True)},'.'"
                                   f",{compute_common_xpath_expr('starts-with', 'Pret', False)}"
                                   f"/sup/small/text())").get().replace('lei', '').strip()
        else:
            price_xpath_expr = compute_common_xpath_expr('contains', 'promo', False) + "/b/span"
            price = response.xpath(f"concat({price_xpath_expr}/text(),'.'"
                                   f",{price_xpath_expr}/sup/small/text())").get().replace('lei', '').strip()

        book['offer'] = {
            'link': response.meta.get('link'),
            'provider': 'Librarie.net',
            'price': float(price),
            'hasStock': True if response.xpath("//td[starts-with(text(),'Disponibilitate')]/text()") is not None
            else False,
            'transportationCost': 15.99
        }
        yield book
