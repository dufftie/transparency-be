from sqlalchemy import create_engine, or_, desc
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from db.helpers.utils import get_db_address
from db.models.models import *

# Load environment variables
load_dotenv()


class DBConnector:
    """Class for managing database connections and operations."""

    def __init__(self):
        """Initialize the database connection using environment variables."""
        self.db_url = get_db_address()
        self.engine = create_engine(self.db_url)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

        # Initialize tables
        Base.metadata.create_all(self.engine)

    def article_exists(self, article_url):
        return (self
                .session
                .query(self
                       .session
                       .query(Article)
                       .filter_by(url=article_url)
                       .exists()
                       )
                .scalar()
                )


    def analysis_exists(self, article_id, model_name):
        return (
            self
            .session
            .query(SentimentAnalysis)
            .filter(
                SentimentAnalysis.model == model_name,
                SentimentAnalysis.article_id == article_id
            )
            .first()
        )

    def insert_analysis_response(self, analysis_response: SentimentAnalysis):
        self.session.add(analysis_response)
        self.session.commit()

    def update_analysis_response(self, analysis_response: SentimentAnalysis):
        existing_record = self.analysis_exists(analysis_response.article_id)

        if existing_record:
            print(f"Updating analysis for article {analysis_response.article_id} with model {analysis_response.model}.")
            existing_record.sentiment = analysis_response.sentiment  # Update sentiment
            self.session.commit()
            return existing_record
        else:
            print(
                f"No existing analysis found for article {analysis_response.article_id} with model {analysis_response.model}.")
            return None

    def insert_or_update_article(self, article: Article):
        try:
            # Check if the article with the same URL already exists
            existing_article = self.session.query(Article).filter(Article.article_id == article.article_id).first()

            if existing_article:  # If article exists, update the 'url' field
                print(f"Article with URL {article.url} already exists. Updating URL field.")
                existing_article.url = article.url  # Update the 'url' field (or any other field)
            else:
                # If article does not exist, insert the new article
                self.session.add(article)

            # Commit the changes
            self.session.commit()
            print(f"Article with URL {article.url} has been inserted or updated.")

        except Exception as e:
            # Rollback the session in case of integrity error
            print("Integrity error:", e)
            self.session.rollback()

    def insert_article_analysis(self, analysis: ArticleAnalysis):
        existing_record = self.session.query(ArticleAnalysis).filter_by(
            sentiment_id=analysis.sentiment_id,
        ).first()

        if not existing_record:
            self.session.add(analysis)
            self.session.commit()

    def insert_parties_analysis(self, analysis: List[PartyAnalysis]):
        for party in analysis:
            existing_record = self.session.query(PartyAnalysis).filter_by(
                sentiment_id=party.sentiment_id,
                name=party.name
            ).first()

            if not existing_record:
                self.session.add(party)

        self.session.commit()

    def insert_politician_analysis(self, analysis: List[PoliticianAnalysis]):
        for politician in analysis:
            existing_record = self.session.query(PoliticianAnalysis).filter_by(
                sentiment_id=politician.sentiment_id,
                name=politician.name
            ).first()

            if not existing_record:
                self.session.add(politician)

        self.session.commit()

    def close(self):
        """Close the session."""
        self.session.close()
