import scrapy
from bookscraper.items import BookItem
from scrapy_splash import SplashRequest


def extract_title(title_and_author, author):
    title_and_author = title_and_author.strip()
    author_start_index = title_and_author.find(author)
    if author_start_index != -1:
        if title_and_author[author_start_index - 1] != ' ':
            return title_and_author[0:author_start_index - 1].strip()

        return title_and_author[0:author_start_index - 2].strip()
    return title_and_author


# TODO implement scraping other offers functionality
class EmagSpider(scrapy.Spider):
    name = 'emag'

    def start_requests(self):
        url = 'https://www.emag.ro/search/9789734648887?ref=effective_search'

        yield SplashRequest(url=url, callback=self.parse, args={'images': 0, 'forbidden_content_types': 'text/css,'
                                                                                                        'font/* '})

    def parse(self, response):
        urls = response.css('div.js-product-data a.thumbnail-wrapper.js-product-url::attr(href)').getall()
        for url in urls:
            yield SplashRequest(url=url, callback=self.parse_book_info, args={'forbidden_content_types': 'text/css,'
                                                                                                         'font/* ',
                                                                              'wait': 1},
                                meta={"url": url})

    def parse_book_info(self, response):
        url = response.meta.get('url')
        scraped_providers = ['Librarie.Net', 'Libris SRL', 'Carturesti', 'Diverta']
        book = BookItem()
        response.xpath("//div[contains(text(),'Vândut')]/child::span/child::a/text()").get()
        provider_response = response.xpath("//div[contains(text(),'Vândut')]/child::span/child::a/text()").get()

        provider = provider_response.strip() if provider_response is not None else None
        if provider is not None and provider not in scraped_providers:
            price_tag_xpath = "//p[@class='product-new-price']"
            book['offer'] = {
                "provider": provider if provider == 'eMAG' else f"{provider} via eMAG",
                "price": float(response.xpath(f"concat({price_tag_xpath}/text(),'.',{price_tag_xpath}/child::sup/text())")
                                       .get().strip()),
                "link": url,
                "hasStock": True if response.xpath("//div[contains(@class, 'product-page-pricing')]/child::span/text()")
                                            .get() is not 'Indisponibil' else False,
                "transportationCost": 19.99
            }

            yield book
