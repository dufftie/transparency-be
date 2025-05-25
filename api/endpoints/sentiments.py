from typing import List, Dict, Any

from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session

from api.utils.db_utils import get_db, check_results, FilterParams
from api.utils.repositories.sentiment_repository import SentimentRepository

router = APIRouter()
sentiment_repository = SentimentRepository()


@router.get("/daily-stats/media/{media_id}")
async def get_daily_article_and_sentiment_stats(
        media_id: int,
        paywall: bool = False,
        start_date: str = None,
        end_date: str = None,
        db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get daily counts of articles and their sentiment analyses"""
    # Log request parameters
    print(
        f"Media IDs: {media_id}, Paywall: {paywall}, Start Date: {start_date}, End Date: {end_date}")

    # Create filter parameters
    filters = FilterParams(
        media_id=media_id,
        paywall=paywall, 
        start_date=start_date,
        end_date=end_date
    )
    
    # Get data from repository
    results = sentiment_repository.get_daily_stats_by_media(db, filters)
    check_results(results)
    
    return results


@router.get("/parties/")
async def get_party_sentiment(
        media_id: int = Query(1),
        parties: List[str] = Query([], description="List of party names"),
        start_date: str = None,
        end_date: str = None,
        paywall: bool = False,
        db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Fetch sentiment data for party mentions and their sentiment scores.
    If parties list is empty, returns sentiment data for all parties.
    """
    # Log request parameters
    print(
        f"Parties: {parties}, Start Date: {start_date}, End Date: {end_date}, Paywall: {paywall}")

    # Create filter parameters
    filters = FilterParams(
        media_id=media_id,
        paywall=paywall,
        start_date=start_date,
        end_date=end_date
    )
    
    # Get data from repository
    results = sentiment_repository.get_party_sentiment(db, parties, filters)
    check_results(results)
    
    return results


@router.get("/parties/summary/")
async def get_party_sentiment_summary(
        media_id: int = Query(...),
        start_date: str = None,
        end_date: str = None,
        paywall: bool = False,
        db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Fetch sentiment data summary for all parties.
    """
    # Log request parameters
    print(
        f"Media ID: {media_id}, Start Date: {start_date}, End Date: {end_date}, Paywall: {paywall}")

    # Create filter parameters
    filters = FilterParams(
        media_id=media_id,
        paywall=paywall,
        start_date=start_date,
        end_date=end_date
    )
    
    # Get data from repository
    results = sentiment_repository.get_party_sentiment_summary(db, filters)
    check_results(results)
    
    return results


@router.get("/parties/progress/")
async def get_party_sentiment_progress(
        media_id: int = Query(...),
        parties: List[str] = Query([], description="List of party names"),
        start_date: str = None,
        end_date: str = None,
        paywall: bool = False,
        db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Fetch sentiment data for party mentions and their sentiment scores.
    If parties list is empty, returns sentiment data for all parties.
    """
    # Log request parameters
    print(
        f"Media ID: {media_id}, Parties: {parties}, Start Date: {start_date}, End Date: {end_date}, Paywall: {paywall}")

    # Create filter parameters
    filters = FilterParams(
        media_id=media_id,
        paywall=paywall,
        start_date=start_date,
        end_date=end_date
    )
    
    # Get data from repository
    results = sentiment_repository.get_party_sentiment_progress(db, parties, filters)
    check_results(results)
    
    return results


@router.get("/summary/")
async def get_sentiment_summary(
        media_id: int = Query(...),
        start_date: str = None,
        end_date: str = None,
        db: Session = Depends(get_db)
) -> Dict[int, int]:
    """
    Get summary of sentiment counts for a media.
    Returns a dictionary where keys are sentiment scores and values are counts.
    """
    # Log request parameters
    print(f"Media ID: {media_id}, Start Date: {start_date}, End Date: {end_date}")

    # Create filter parameters
    filters = FilterParams(
        media_id=media_id,
        start_date=start_date,
        end_date=end_date
    )
    
    # Get data from repository
    results = sentiment_repository.get_sentiment_summary(db, filters)
    
    return results


@router.get("/politicians/summary/")
async def get_politician_mention_summary(
        media_id: int = Query(...),
        start_date: str = None,
        end_date: str = None,
        paywall: bool = False,
        limit: int = Query(10, description="Number of most mentioned politicians to return"),
        db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Fetch sentiment data summary for most mentioned politicians.
    Returns a list of politicians with their sentiment score distribution, limited to N most mentioned.
    """
    # Log request parameters
    print(
        f"Media ID: {media_id}, Start Date: {start_date}, End Date: {end_date}, Paywall: {paywall}, Limit: {limit}")

    # Create filter parameters
    filters = FilterParams(
        media_id=media_id,
        paywall=paywall,
        start_date=start_date,
        end_date=end_date
    )
    
    # Get data from repository
    results = sentiment_repository.get_politician_mention_summary(db, filters, limit)
    check_results(results)
    
    return results