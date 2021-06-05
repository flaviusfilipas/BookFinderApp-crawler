import scrapy
from bookscraper.items import BookItem
from scrapy_splash import SplashRequest


def get_offer(response):
    price = response.xpath("concat(//span[contains(@class,'pret')]/text(),'',//span[@class='bani']/text())").get() \
        .strip()
    return {
        'link': response.meta.get('link'),
        'provider': 'Carturesti',
        'price': float(price) if price is not None else None,
        'hasStock': True if response.css("span.stocText::text").get() != 'Indisponibil' else False,
        'transportationCost': 19.90
    }


lua_script = """
    function main(splash)
        assert(splash:go(splash.args.url))
        
        function wait_for(splash, condition)
            while not condition() do
                splash:wait(0.2)
            end
        end
        
        wait_for(splash, function()
            return splash:evaljs("document.evaluate(\\"//span[starts-with(text(),'ISBN')]/following-sibling::div/text()\\",document,null,XPathResult.STRING_TYPE,null).stringValue !== ''")
        end)
        
        return splash:html()
    end
"""


class CarturestiSpider(scrapy.Spider):
    name = "carturesti"

    # only for testing purposes. url will be passed through scrapyrt as a param
    def start_requests(self):
        url = f'https://carturesti.ro/product/search/Sapiens?page=1&id_product_type=26'
        yield SplashRequest(url=url, dont_filter=True, callback=self.parse,
                            args={'wait': 1, 'forbidden_content_types': 'text/css,font/*',
                                  'filters': 'easylist'})

    def parse(self, response):
        books = response.css('div.cartu-grid-tile')
        base_url = 'https://carturesti.ro'
        for b in books:
            book = BookItem()
            book['title'] = b.css('h5::text').get()
            book['author'] = b.css('div.subtitlu-produs a::text').get()
            book['imgUrl'] = b.css('div.productImageContainer img::attr(src)').get()
            individual_book_url = b.css('a::attr(href)').get()
            book_link = f'{base_url}{individual_book_url}'
            yield SplashRequest(url=book_link,
                                dont_filter=True,
                                endpoint='execute',
                                callback=self.parse_book_info,
                                args={'lua_source': lua_script, 'wait': 1, 'images': 0,
                                      'forbidden_content_types': 'text/css,font/* ',
                                      'filters': 'easylist'},
                                meta={'book': book, 'link': book_link})

    def parse_book_info(self, response):
        book = response.meta.get('book')
        publisher = response.xpath("//span[contains(text(),'Editura: ')]/following-sibling::div/span/a/text()") \
            .get()
        book['publisher'] = publisher.strip() if publisher is not None else None
        book['numberOfPages'] = response.xpath("//span[starts-with(text(),'Nr')]/following-sibling::div/text()").get()
        book['isbn'] = response.xpath("//span[starts-with(text(),'ISBN')]/following-sibling::div/text()").get()
        cover_type = response.xpath("//span[starts-with(text(),'Tip')]/following-sibling::div/text()").get()
        book['coverType'] = cover_type.strip() if cover_type is not None else None
        book['offer'] = get_offer(response)
        yield book

    def parse_simple_book_info(self, response):
        yield get_offer(response)
