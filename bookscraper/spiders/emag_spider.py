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
        url = 'https://www.emag.ro/search/Sapiens%20carte?ref=effective_search'

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
        provider_xpath = "//span[@class='text-label'][contains(text(),'Vândut')]/parent::div/following-sibling::div"
        provider = response.xpath(f"{provider_xpath}/text()").get().strip()
        if provider == '':
            provider = response.xpath(f"{provider_xpath}/child::a/text()").get().strip()
        if provider not in scraped_providers:
            title_and_author = response.css("h1.page-title::text").get()
            author = response.xpath("//td[starts-with(text(),'Autor')]/following-sibling::td/text()").get().strip()
            if '\n' in author:
                author_list = author.split('\n')
                book['title'] = extract_title(title_and_author, author_list[0])
                book['author'] = author.replace("\n", ",").strip()
            else:
                book['title'] = extract_title(title_and_author, author)
                book['author'] = author

            price_tag_xpath = "//p[@class='product-new-price']"
            book['imgUrl'] = response.css("a.thumbnail.product-gallery-image::attr(href)").get()
            book['isbn'] = response.xpath("//td[contains(text(),'ISBN')]/following-sibling::td/text()").get().strip()
            book['coverType'] = response.xpath(
                "//td[starts-with(text(),'Tip')]/following-sibling::td/text()").get().strip()
            book['numberOfPages'] = response.xpath(
                "//td[starts-with(text(),'Numar')]/following-sibling::td/text()").get().strip()
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
