from urllib.parse import urlparse, quote, parse_qs, urlencode, urlunparse

import scrapy
from lib.crawler.items import ArticleItem
from db.db_connector import DBConnector


class BasePostimeesSpider(scrapy.Spider):
    name = None  # Must be defined in subclass
    media_id = None  # Must be defined in subclass
    base_url = None  # Must be defined in subclass
    next_page_selector = None  # Must be defined in subclass
    last_scrapped_article = None
    prohibited_subdomains = [
        'prognoz',
        'zdorovje',
        'limon',
        'sport',
        'elu24',
        'saartehaal',
        'naine',
        'kodu',
        'wallstreetjournal',
        'tv',
        'kultuur',
        'purjetamine',
        'kuuuurija',
        'ilmajaam',
        'naine',
        'tervis',
        'reis',
        'raamatud',
        'lemmik',
        'digiajakirjad',
        'reporter',
        'sakala',
        '60pluss',
        'meeldib',
        'maaelu',
        'teadus',
        'tehnika',
        'tartu',
        'maailm',
        'jarvateataja',
        'lounapostimees',
        'parnu',
        'haridus'
    ]

    def __init__(self, *args, **kwargs):
        super(BasePostimeesSpider, self).__init__(*args, **kwargs)
        print("Initialized crawler for media:", self.media_id)
        self.db = DBConnector()
        self.start_urls = [self.base_url]

    def start_requests(self):
        print("start_requests", self.start_urls)
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        """Parse the search results page and follow article links."""
        articles = response.css("article a::attr(href)")
        if articles is None:
            return

        for article in articles:
            article_url = article.get()
            parsed_url = urlparse(article_url)
            subdomain = parsed_url.netloc.split(".")[0]

            if subdomain not in self.prohibited_subdomains and not self.db.article_exists(article_url):
                yield response.follow(article_url, self.parse_article)

        next_page = response.xpath(self.next_page_selector).get()
        if next_page is not None:
            print('Following next page:', next_page)
            yield response.follow(next_page, self.parse)
        else:
            formatted_datetime = self.last_scrapped_article['date_time'].strftime("%Y-%m-%dT23:59:59+02:00")

            parsed_url = urlparse(self.base_url)
            query_params = parse_qs(parsed_url.query)
            query_params["end"] = [formatted_datetime]

            new_query_string = urlencode(query_params, doseq=True)
            updated_url = urlunparse(parsed_url._replace(query=new_query_string))

            print(
                'Next page not found, adding time variable from the last scrapped article:',
                updated_url, self.last_scrapped_article['date_time']
            )
            yield response.follow(str(updated_url), self.parse)

    def parse_article(self, response):
        """Parse the article page and extract details."""
        article = ArticleItem()

        article['article_id'] = response.css('meta[name="cXenseParse:articleId"]::attr(content)').get()
        article['media_id'] = self.media_id
        article['url'] = response.url
        article['date_time'] = response.css('.article__publish-date::attr(content)').get()
        article['authors'] = response.css('.author .author__name::text').get()
        article['paywall'] = response.css('.article__premium-flag')
        article['category'] = response.css("ul.breadcrumb__items li.breadcrumb-item:last-child a::text").get()
        article['preview_url'] = response.css(".figure__image-wrapper img::attr(src)").get()

        title = response.css('.article__headline::text').get()
        if not title:
            title = response.css('.article-superheader__headline::text').get()
        article['title'] = title

        article['body'] = response.css('.article-body-content p ::text').getall()

        self.last_scrapped_article = article
        yield article
