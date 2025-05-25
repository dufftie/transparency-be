import json
import re
import time
from abc import abstractmethod
from typing import List

from db.db_connector import DBConnector
from db.models.models import Article, SentimentAnalysis
from db.parsers.sentiment_parser import SentimentParser
from lib.crawler.helpers.utils import format_article_request


class SentimentBaseAnalyzer:
    """Sentiment Analyzer is an abstract interface to """

    def __init__(self, model_name: str):
        """Initialize the sentiment analyzer and configure the model"""
        self.model_name = model_name
        self.db = DBConnector()
        print(f"Initializing '{model_name}' model for article analysis'")

    @abstractmethod
    def send_message(self, text: str):
        pass

    @staticmethod
    def parse_sentiment(response: json):
        if isinstance(response, str):
            cleaned_response = re.sub(r",\s*([}\]])", r"\1", response)

            try:
                parsed_json = json.loads(cleaned_response)
                return parsed_json
            except json.JSONDecodeError as e:
                print(f"JSON decoding error: {e}")
                return None
        else:
            parsed_json = response
            return parsed_json

    def check_if_analysis_exists(self, article: Article):
        analysis_found = self.db.analysis_exists(article.id, self.model_name)
        if analysis_found:
            print(f"Analyses found for article '{article.title}'. Skipping article...")
            return analysis_found
        return None

    def request_sentiment_analysis(self, article):
        print(f"Analysis for article '{article.title}' wasn't found. Making a request...")

        retries = 0
        max_retries = 3
        retry_delay = 30
        while retries < max_retries:
            try:
                response = self.send_message(format_article_request(article.media_id, article.title, article.body))
                analysis = SentimentAnalysis(
                    article_id=article.id,
                    model=self.model_name,
                    sentiment=self.parse_sentiment(response)
                )
                return analysis
            except Exception as e:
                retries += 1
                print(f"Error analyzing '{article.title}': {e}")
                if retries < max_retries:
                    print(f"Retrying in {retry_delay} seconds... ({retries}/{max_retries})")
                    time.sleep(retry_delay)
                else:
                    print(f"Skipping '{article.title}' after {max_retries} failed attempts.")
        return None

    def analyze(self, articles: List[Article]):
        print(f"Analyzing scope is {len(articles)} articles...")
        parser = SentimentParser()

        for article in articles:
            print(f"Analyzing article: {article.title} ({article.id})...")

            analysis = self.check_if_analysis_exists(article)
            if not analysis:
                analysis = self.request_sentiment_analysis(article)
                self.db.insert_analysis_response(analysis)

            try:
                parser.sync_analysis(analysis)
            except TypeError as e:
                print("Type error in returned analysis: ", e)
                print("Will try to rewrite result")

                try:
                    analysis = self.db.update_analysis_response(self.request_sentiment_analysis(article))
                    parser.sync_analysis(analysis)
                except Exception as e:
                    print(f"Did not succeed to override sentiment analysis for: {article.title}({article.id})", e)

        print("All articles were analyzed")
