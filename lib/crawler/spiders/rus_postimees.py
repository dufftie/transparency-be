from lib.crawler.spiders.base_postimees import BasePostimeesSpider


class RusPostimeesSpider(BasePostimeesSpider):
    media_id = 1
    name = "rus.postimees"
    base_url = "https://rus.postimees.ee/search?sections=455&start=1970-01-01T01%3A00%3A00%2B03%3A00&fields=body%2Cauthors%2Cheadline%2Ckeywords"
    next_page_selector = "//a[text()='Далее ']/@href"
