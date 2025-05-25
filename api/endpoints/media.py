from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import joinedload, Session

from api.utils.db_utils import get_db_session
from db.models.models import Media, ChiefEditorHistory, SentimentAnalysis, Article

router = APIRouter()


@router.get("/")
async def get_media_list(db: Session = Depends(get_db_session)):
    """
    Fetch list of media along with the count of analyzed and total articles.
    """
    media_list = (
        db.query(
            Media,
            func.count(Article.id).label("total_count"),
            func.count(SentimentAnalysis.id).label("analyzed_count"),
        )
        .outerjoin(Article, Article.media_id == Media.id)
        .outerjoin(SentimentAnalysis, SentimentAnalysis.article_id == Article.id)
        .options(joinedload(Media.chief_editors))
        .group_by(Media.id, Media.title, Media.base_url, Media.description, Media.slug, Media.language_code)
        .all()
    )

    # Convert result to a list of dictionaries
    result = [
        {
            "id": media.id,
            "title": media.title,
            "slug": media.slug,
            "description": media.description,
            "total_count": total_count,
            "analyzed_count": analyzed_count,
            "language_code": media.language_code,
            "editors": media.chief_editors,
        }
        for media, total_count, analyzed_count in media_list
    ]

    return {"media": result}


@router.get("/{media_slug}/")
async def get_media(media_slug: str):
    """
    Fetch basic article information for tooltip display
    """
    # Log request parameters
    print(f"Media slug: {media_slug}")

    session = get_db_session()

    # Start with the base query
    result = (
        session
        .query(
            Media,
            func.count(Article.id).label("total_count"),
            func.count(SentimentAnalysis.id).label("analyzed_count"),
        )
        .outerjoin(Article, Article.media_id == Media.id)
        .outerjoin(SentimentAnalysis, SentimentAnalysis.article_id == Article.id)
        .filter(Media.slug == media_slug)
        .group_by(Media.id, Media.title, Media.base_url, Media.description, Media.slug, Media.language_code)
        .first()
    )
    
    # Check if media exists
    if result is None:
        raise HTTPException(status_code=404, detail=f"Media with slug '{media_slug}' not found")
    
    media, total_count, analyzed_count = result

    chief_editors = (
        session
        .query(ChiefEditorHistory)
        .filter(ChiefEditorHistory.media_id == media.id)
        .all()
    )

    # Prepare the result data
    return {
        "media": media,
        "chief_editors": chief_editors,
        "total_count": total_count,
        "analyzed_count": analyzed_count,
    }
