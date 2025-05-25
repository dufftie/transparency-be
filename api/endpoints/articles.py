from typing import Dict, Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from api.utils.db_utils import get_db, check_results
from api.utils.repositories.article_repository import ArticleRepository
from db.models.models import Article, SentimentAnalysis

router = APIRouter()
article_repository = ArticleRepository()


@router.get("/{article_id}/tooltip")
async def get_article_tooltip(article_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Fetch basic article information for tooltip display
    """
    # Log request parameters
    print(f"Article id: {article_id}")

    # Get tooltip data from repository
    result = article_repository.get_with_tooltip(db, article_id)
    check_results(result)

    return result


@router.get("/{article_id}/")
async def get_article_detail(article_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Fetch detailed article information including sentiments and media details.
    """
    print(f"Article id: {article_id}")

    # Get full article details from repository
    result = article_repository.get_full_article_detail(db, article_id)
    check_results(result)

    return result


@router.get("/stats")
async def get_article_stats(db: Session = Depends(get_db)):
    """
    Fetch total count of articles and total count of sentiment analyses.
    This is used on page load to avoid recalculating these values on every search request.
    """
    total_articles = db.query(Article.id).distinct().count()
    total_sentiments = db.query(SentimentAnalysis.id).count()

    return {
        "total_articles": total_articles,
        "total_sentiments": total_sentiments
    }


@router.get("/search")
async def search_articles(value: str, limit: int = 20, db: Session = Depends(get_db)):
    """
    Perform a full-text search in the 'articles' table.
    Returns only articles that have corresponding entries in the 'SentimentAnalysis' table.
    Additionally, the results are sorted by article.date_time from newest to oldest.
    """

    query = text(f"""
                 SELECT a.id, a.title, a.category, a.date_time, m.title AS media_title
                 FROM articles a
                          JOIN sentiment_analysis sa ON sa.article_id = a.id
                          LEFT JOIN medias m ON a.media_id = m.id
                 WHERE to_tsvector('simple', a.title) @@ to_tsquery('simple', :search_query)
                 ORDER BY a.date_time DESC
                     LIMIT {limit};
                 """)

    # Convert the search value to PostgreSQL tsquery format
    search_query = value.replace('*', ':*').replace(' ', ' & ')

    result = db.execute(query, {"search_query": search_query}).fetchall()

    articles = [{
        "id": row[0],
        "title": row[1],
        "category": row[2],
        "date_time": row[3],
        "media_title": row[4]
    } for row in result]

    return {"articles": articles}