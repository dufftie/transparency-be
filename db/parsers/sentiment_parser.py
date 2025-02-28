from typing import List

from db.db_connector import DBConnector
from db.models.models import *


class SentimentParser:
    def __init__(self, media_id):
        self.media_id = media_id
        self.db = DBConnector(self.media_id)

    def sync_analysis(self, analysis: SentimentAnalysis):
        print("Syncing analysis...")

        article_analysis = self.parse_article_analysis(analysis)
        self.db.insert_article_analysis(article_analysis)

        parties_analysis = self.parse_parties_analysis(analysis)
        self.db.insert_parties_analysis(parties_analysis)

        politicians_analysis = self.parse_politicians_analysis(analysis)
        self.db.insert_politician_analysis(politicians_analysis)

    @staticmethod
    def parse_article_analysis(response: SentimentAnalysis) -> ArticleAnalysis:
        return ArticleAnalysis(
            sentiment_id=response.id,
            title_score=response.sentiment['article']['title']['score'],
            title_explanation=response.sentiment['article']['title']['explanation'],
            body_score=response.sentiment['article']['body']['score'],
            body_explanation=response.sentiment['article']['body']['explanation']
        )

    @staticmethod
    def parse_parties_analysis(response: SentimentAnalysis) -> List[PartyAnalysis]:
        return [
            PartyAnalysis(
                sentiment_id=response.id,
                name=party['name'],
                score=party['score'],
                explanation=party['explanation'],
            ) for party in response.sentiment["parties"]
        ]

    @staticmethod
    def parse_politicians_analysis(response: SentimentAnalysis) -> List[PoliticianAnalysis]:
        return [
            PoliticianAnalysis(
                sentiment_id=response.id,
                name=politician['name'],
                score=politician['score'],
                explanation=politician['explanation'],
            ) for politician in response.sentiment["politicians"]
        ]
