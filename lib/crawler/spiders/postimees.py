from lib.crawler.spiders.base_postimees import BasePostimeesSpider


class RusPostimeesSpider(BasePostimeesSpider):
    media_id = 2
    name = "postimees"
    base_url = "https://www.postimees.ee/search?sections=81%2C127%2C517&start=1970-01-01T01%3A00%3A00%2B03%3A00&fields=body%2Cauthors%2Cheadline%2Ckeywords"
    next_page_selector = "//a[text()='Järgmine ']/@href"
