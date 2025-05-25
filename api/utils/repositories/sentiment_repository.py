from typing import List, Dict, Any
from collections import defaultdict
import json

from sqlalchemy.orm import Session
from sqlalchemy import func, case, text

from api.utils.db_utils import BaseRepository, FilterParams, QueryBuilder
from db.models.models import Article, SentimentAnalysis, PartyAnalysis, PoliticianAnalysis


class SentimentRepository(BaseRepository[SentimentAnalysis]):
    """Repository for handling SentimentAnalysis operations"""

    def __init__(self):
        super().__init__(SentimentAnalysis)

    def get_daily_stats_by_media(
        self,
        db: Session,
        filters: FilterParams
    ) -> List[Dict[str, Any]]:
        """Get daily article counts with analysis status by media"""
        # Base query to count articles per day
        query = (
            db.query(
                func.date(Article.date_time).label("date"),
                func.count(Article.id).label("articles_count"),
                func.coalesce(func.count(SentimentAnalysis.id), 0).label("analysed_count")
            )
            .outerjoin(
                SentimentAnalysis,
                (SentimentAnalysis.article_id == Article.id)
            )
            .group_by(func.date(Article.date_time))
            .order_by(func.date(Article.date_time).asc())
        )

        # Apply common filters
        query = QueryBuilder.apply_filters(query, Article, filters)

        # Fetch results
        results = query.all()

        # Format response
        return [
            {
                "date": str(date),
                "articles_count": articles_count,
                "analysed_count": analysed_count,
            }
            for date, articles_count, analysed_count in results
        ]

    def get_party_sentiment(
        self,
        db: Session,
        parties: List[str],
        filters: FilterParams
    ) -> List[Dict[str, Any]]:
        """Get party sentiment data"""
        # Start with the base query
        query = (
            db.query(
                Article.id.label('article_id'),
                PartyAnalysis.name.label("party"),
                PartyAnalysis.score.label("sentiment_score"),
                Article.date_time.label("date")
            )
            .join(SentimentAnalysis, SentimentAnalysis.id == PartyAnalysis.sentiment_id)
            .join(Article, Article.id == SentimentAnalysis.article_id)
        )

        # Apply common filters
        query = QueryBuilder.apply_filters(query, Article, filters)

        # Apply party filter
        if parties:
            query = query.filter(PartyAnalysis.name.in_(parties))

        query = query.order_by(Article.date_time.asc())

        # Execute the query
        results = query.all()

        # Format response
        return [
            {
                "article_id": article_id,
                "party": party,
                "sentiment_score": sentiment_score,
                "date": date.date()  # Only include the date part for scatter plot
            }
            for article_id, party, sentiment_score, date in results
        ]

    def get_party_sentiment_summary(
        self,
        db: Session,
        filters: FilterParams
    ) -> List[Dict[str, Any]]:
        """Get party sentiment summary with score distribution for all parties"""
        # Start with the base query
        query = (
            db.query(
                PartyAnalysis.name.label("party"),
                PartyAnalysis.score.label("sentiment_score")
            )
            .join(SentimentAnalysis, SentimentAnalysis.id == PartyAnalysis.sentiment_id)
            .join(Article, Article.id == SentimentAnalysis.article_id)
        )

        # Apply common filters
        query = QueryBuilder.apply_filters(query, Article, filters)

        # Execute the query
        results = query.all()

        # Format response using dictionary to count scores
        # Prepare a structure to store the sentiment score counts for each party
        party_sentiment_data = defaultdict(lambda: defaultdict(int))

        # Process the results and count the sentiment scores
        for party, sentiment_score in results:
            try:
                sentiment_score = int(sentiment_score)  # Assuming score is a string, cast it to an int
                if 0 <= sentiment_score <= 10:  # Only count scores in the range 0-10
                    party_sentiment_data[party][sentiment_score] += 1
            except ValueError:
                continue  # Skip invalid sentiment scores

        # Prepare the result data in the desired format
        return [
            {
                "name": party,
                **{f"{score}": count for score, count in sentiment_scores.items()}
            }
            for party, sentiment_scores in party_sentiment_data.items()
        ]

    def get_party_sentiment_progress(
        self,
        db: Session,
        parties: List[str],
        filters: FilterParams
    ) -> List[Dict[str, Any]]:
        """Get sentiment progress over time for specified parties"""
        # Base query to get sentiment scores over time
        query = (
            db.query(
                func.to_char(Article.date_time, 'YYYY-MM').label("date"),
                PartyAnalysis.name.label("party"),
                *[func.count(case((PartyAnalysis.score == str(i), 1))).label(str(i)) for i in range(11)]
            )
            .join(SentimentAnalysis, SentimentAnalysis.id == PartyAnalysis.sentiment_id)
            .join(Article, Article.id == SentimentAnalysis.article_id)
            .group_by("date", "party")
            .order_by("date")
        )

        # Apply party filter if specified
        if parties:
            query = query.filter(PartyAnalysis.name.in_(parties))

        # Apply common filters
        query = QueryBuilder.apply_filters(query, Article, filters)

        # Execute the query
        results = query.all()

        # Format response
        return [
            {
                "date": row[0],
                "party": row[1],
                **{str(i): row[i + 2] for i in range(11)}
            }
            for row in results
        ]

    def get_sentiment_summary(
        self,
        db: Session,
        filters: FilterParams
    ) -> Dict[int, int]:
        """Get summary of sentiment counts for a media"""
        # Start with the base query
        query = (
            db.query(
                PartyAnalysis.score.label("sentiment_score"),
                func.count(PartyAnalysis.id).label("count")
            )
            .join(SentimentAnalysis, SentimentAnalysis.id == PartyAnalysis.sentiment_id)
            .join(Article, Article.id == SentimentAnalysis.article_id)
            .group_by(PartyAnalysis.score)
        )

        # Apply common filters
        query = QueryBuilder.apply_filters(query, Article, filters)

        # Execute the query
        results = query.all()

        # Format response as a dictionary with sentiment score as key and count as value
        return {int(score): count for score, count in results if score is not None}

    def get_politician_mention_summary(
        self,
        db: Session,
        filters: FilterParams,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get politician sentiment summary with score distribution for most mentioned politicians"""
        # First, get the total mention count for each politician
        mention_counts = (
            db.query(
                PoliticianAnalysis.name.label("politician"),
                func.count(PoliticianAnalysis.id).label("total_mentions")
            )
            .join(SentimentAnalysis, SentimentAnalysis.id == PoliticianAnalysis.sentiment_id)
            .join(Article, Article.id == SentimentAnalysis.article_id)
            .filter(Article.media_id == filters.media_id)
            .group_by(PoliticianAnalysis.name)
            .order_by(func.count(PoliticianAnalysis.id).desc())
            .limit(limit)
            .all()
        )

        # Get the list of top N politicians
        top_politicians = [name for name, _ in mention_counts]

        # Now get the sentiment distribution for these politicians
        query = (
            db.query(
                PoliticianAnalysis.name.label("politician"),
                PoliticianAnalysis.score.label("sentiment_score")
            )
            .join(SentimentAnalysis, SentimentAnalysis.id == PoliticianAnalysis.sentiment_id)
            .join(Article, Article.id == SentimentAnalysis.article_id)
            .filter(PoliticianAnalysis.name.in_(top_politicians))
        )

        # Apply common filters
        query = QueryBuilder.apply_filters(query, Article, filters)

        # Execute the query
        results = query.all()

        # Format response using dictionary to count scores
        # Prepare a structure to store the sentiment score counts for each politician
        politician_sentiment_data = defaultdict(lambda: defaultdict(int))

        # Process the results and count the sentiment scores
        for politician, sentiment_score in results:
            try:
                sentiment_score = int(sentiment_score)  # Assuming score is a string, cast it to an int
                if 0 <= sentiment_score <= 10:  # Only count scores in the range 0-10
                    politician_sentiment_data[politician][sentiment_score] += 1
            except ValueError:
                continue  # Skip invalid sentiment scores

        # Prepare the result data in the desired format
        return [
            {
                "name": politician,
                **{f"{score}": count for score, count in sentiment_scores.items()}
            }
            for politician, sentiment_scores in politician_sentiment_data.items()
        ]