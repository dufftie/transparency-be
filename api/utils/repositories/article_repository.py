from typing import Dict, Any

from sqlalchemy.orm import Session

from api.utils.db_utils import BaseRepository
from db.models.models import (
    Article, 
    ArticleAnalysis, 
    PoliticianAnalysis, 
    PartyAnalysis, 
    SentimentAnalysis, 
    Media
)


class ArticleRepository(BaseRepository[Article]):
    """Repository for handling Article operations"""
    
    def __init__(self):
        super().__init__(Article)
    
    def get_with_tooltip(self, db: Session, article_id: str) -> Dict[str, Any]:
        """Get tooltip data for an article"""
        article = self.get(db, article_id)
        
        if not article:
            return None
            
        return article.to_tooltip_dict()
    
    def get_full_article_detail(self, db: Session, article_id: str) -> Dict[str, Any]:
        """Get detailed article data with all related entities"""
        # Fetch Article
        article = self.get(db, article_id)
        if not article:
            return None
            
        # Fetch Media
        media = db.query(Media).filter(Media.id == article.media_id).first()
        if not media:
            return None
            
        # Fetch SentimentAnalysis rows
        sentiments = (
            db.query(SentimentAnalysis)
            .filter(SentimentAnalysis.article_id == article.id)
            .all()
        )
        sentiment_ids = [s.id for s in sentiments]
        
        # Preload all analyses
        article_analyses = (
            db.query(ArticleAnalysis)
            .filter(ArticleAnalysis.sentiment_id.in_(sentiment_ids))
            .all()
        )
        party_analyses = (
            db.query(PartyAnalysis)
            .filter(PartyAnalysis.sentiment_id.in_(sentiment_ids))
            .all()
        )
        politician_analyses = (
            db.query(PoliticianAnalysis)
            .filter(PoliticianAnalysis.sentiment_id.in_(sentiment_ids))
            .all()
        )
        
        # Organize analyses by sentiment_id
        article_analysis_map = {a.sentiment_id: a.to_dict() for a in article_analyses}
        
        party_analysis_map = {}
        for p in party_analyses:
            party_analysis_map.setdefault(p.sentiment_id, []).append(p.to_dict())
        
        politician_analysis_map = {}
        for p in politician_analyses:
            politician_analysis_map.setdefault(p.sentiment_id, []).append(p.to_dict())
        
        # Compose sentiments array
        sentiments_data = []
        for sentiment in sentiments:
            sid = sentiment.id
            sentiments_data.append(
                sentiment.to_full_dict(
                    article_analysis=article_analysis_map.get(sid, {}),
                    party_analyses=party_analysis_map.get(sid, []),
                    politician_analyses=politician_analysis_map.get(sid, [])
                )
            )
        
        # Final response:
        return {
            "article": article.to_detail_dict(),
            "media": media.to_dict(),
            "sentiments": sentiments_data
        }