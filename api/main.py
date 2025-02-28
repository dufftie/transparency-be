# uvicorn api.main:app --reload
from typing import List, Optional

from fastapi import FastAPI, Query

from db.db_connector import DBConnector
from db.models.models import *

app = FastAPI()


@app.get("/category")
async def get_category_data(
        category: str,
        media_id: Optional[List[int]] = Query(None),
        paywall: Optional[bool] = Query(None),
):
    db = DBConnector(media_id=1)
    query = db.session.query(Article, SentimentAnalysis, ArticleAnalysis) \
        .join(SentimentAnalysis, SentimentAnalysis.article_id == Article.article_id) \
        .join(ArticleAnalysis, ArticleAnalysis.sentiment_id == SentimentAnalysis.id) \
        .filter(Article.category == category)

    # Apply the media_id filter if provided
    if media_id:
        query = query.filter(Article.media_id.in_(media_id))

    # Apply the paywall filter if provided
    if paywall is not None:
        query = query.filter(Article.paywall == paywall)

    result = query.first()  # Get the first matching result

    if not result:
        raise HTTPException(status_code=404, detail="No data found for the given parameters")

    # Extracting the data
    article, sentiment_analysis, article_analysis = result

    # Prepare the response data
    response_data = {
        "article_id": article.article_id,
        "title": article.title,
        "category": article.category,
        "url": article.url,
        "sentiment_model": sentiment_analysis.model,
        "sentiment": sentiment_analysis.sentiment,
        "title_score": article_analysis.title_score,
        "title_explanation": article_analysis.title_explanation,
        "body_score": article_analysis.body_score,
        "body_explanation": article_analysis.body_explanation,
    }

    return response_data
