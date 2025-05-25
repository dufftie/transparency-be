# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import os
from urllib.parse import urlencode
from dotenv import load_dotenv
from scrapy import signals

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter


class SpidersSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class ScraperAPIMiddleware:
    """
    Middleware to handle request proxying through ScraperAPI service.
    
    This middleware modifies the request URL to use ScraperAPI's proxy service.
    It adds the API key and other configuration options to the request.
    """
    
    @classmethod
    def from_crawler(cls, crawler):
        # Initialize middleware from crawler
        middleware = cls()
        crawler.signals.connect(middleware.spider_opened, signal=signals.spider_opened)
        return middleware
        
    def process_request(self, request, spider):
        # Skip if this request already has a proxy applied
        # This makes it compatible with rotating_proxies middleware
        if request.meta.get("proxy"):
            spider.logger.debug(f"Request already has a proxy, skipping ScraperAPI for: {request.url}")
            return None
            
        if request.meta.get("proxy_applied"):
            return None
        
        # Load the API key from environment
        load_dotenv()
        api_key = os.getenv("SCRAPER_API_KEY")
        
        if not api_key:
            spider.logger.error("No ScraperAPI key found in .env file!")
            return None
            
        # Original URL
        original_url = request.url
        
        # Parameters for ScraperAPI
        params = {
            "api_key": api_key,
            "url": original_url,
            "country_code": "ee",  # Estonia, change as needed
            "keep_headers": "true"
        }
        
        # Create the proxy URL - we make request directly to scraperapi instead of the target URL
        proxy_url = "https://api.scraperapi.com/"
        
        # Add parameters to the request - they'll be sent as query parameters
        request._set_url(f"{proxy_url}?{urlencode(params)}")
        
        # Store the parameters and original URL for reference
        request.meta['scraperapi_params'] = params
        request.meta['original_url'] = original_url
        
        # Mark this request as having been processed by this middleware
        request.meta["proxy_applied"] = True
        
        spider.logger.debug(f"Using ScraperAPI proxy for: {original_url}")
        
        return None
        
    def spider_opened(self, spider):
        spider.logger.info("ScraperAPIMiddleware initialized")


class SpidersDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)
