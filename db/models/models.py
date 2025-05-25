from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime, Boolean, String, Date, func, JSON, UniqueConstraint, \
    Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from typing import List, Dict, Any, Optional

Base = declarative_base()


class Article(Base):
    """
    Model representing news articles.
    """
    __tablename__ = 'articles'
    id = Column(Integer, primary_key=True, autoincrement=True)
    article_id = Column(Integer, nullable=False)
    media_id = Column(Integer, ForeignKey('medias.id'), nullable=False)
    url = Column(Text, nullable=False)
    title = Column(Text, nullable=False)
    date_time = Column(DateTime, nullable=False)
    authors = Column(Text)
    paywall = Column(Boolean, nullable=False)
    category = Column(String(100))
    preview_url = Column(String(255))
    body = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())

    __table_args__ = (
        UniqueConstraint('article_id', 'media_id', name='uq_article_media'),
        Index('ix_title', 'title')  # PostgreSQL compatible index
    )

    def to_tooltip_dict(self) -> Dict[str, Any]:
        """Convert article to tooltip format dictionary"""
        return {
            "authors": self.authors,
            "category": self.category,
            "date_time": self.date_time,
            "paywall": self.paywall,
            "title": self.title,
            "preview_url": self.preview_url,
        }

    def to_detail_dict(self) -> Dict[str, Any]:
        """Convert article to detail dictionary"""
        return {
            "id": self.id,
            "title": self.title,
            "body": self.body,
            "category": self.category,
            "authors": self.authors,
            "preview_url": self.preview_url,
            "url": self.url,
            "created_at": self.created_at,
            "date_time": self.date_time.isoformat() if self.date_time else None,
        }


class Media(Base):
    """
    Model representing media sources (newspapers, websites, etc).
    """
    __tablename__ = 'medias'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    base_url = Column(String(255), nullable=False)
    description = Column(Text)
    slug = Column(String(255), unique=True, nullable=False)
    language_code = Column(String(8))

    chief_editors = relationship(
        "ChiefEditorHistory",
        back_populates="media",
        cascade="all, delete-orphan"
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert media to dictionary"""
        return {
            "id": self.id,
            "title": self.title,
            "slug": self.slug,
        }


class ChiefEditorHistory(Base):
    """
    Model tracking the history of chief editors for media sources.
    """
    __tablename__ = 'chief_editor_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    media_id = Column(Integer, ForeignKey('medias.id'), nullable=False)
    name = Column(String(255), nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)
    media = relationship("Media", back_populates="chief_editors")


class Parties(Base):
    """
    Model representing political parties.
    """
    __tablename__ = 'parties'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    aliases = Column(Text)


class Politicians(Base):
    """
    Model representing individual politicians.
    """
    __tablename__ = 'politicians'
    id = Column(Integer, primary_key=True, autoincrement=True)
    personal_id = Column(Integer)
    title = Column(String(255), nullable=False)
    aliases = Column(Text)
    current_party = Column(Integer, ForeignKey('parties.id'))


class SentimentAnalysis(Base):
    """
    Model for storing sentiment analysis results.
    """
    __tablename__ = 'sentiment_analysis'
    id = Column(Integer, primary_key=True, autoincrement=True)
    article_id = Column(Integer, ForeignKey('articles.id'), nullable=False)
    model = Column(String(25), nullable=False)
    sentiment = Column(JSONB, nullable=False)  # Using PostgreSQL's native JSONB type
    analysed_at = Column(DateTime, default=func.now())

    def to_dict(self) -> Dict[str, Any]:
        """Convert sentiment analysis to dictionary"""
        return {
            "id": self.id,
            "model": self.model,
            "analysed_at": self.analysed_at,
        }

    def to_full_dict(self, article_analysis: Optional[Dict] = None,
                     party_analyses: Optional[List[Dict]] = None,
                     politician_analyses: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """Convert sentiment analysis to full dictionary with related analyses"""
        base_dict = self.to_dict()

        # Add sentiment details
        base_dict["sentiment"] = {
            "article": article_analysis or {},
            "parties": party_analyses or [],
            "politicians": politician_analyses or []
        }

        return base_dict


class ArticleAnalysis(Base):
    """
    Model for detailed article sentiment analysis.
    """
    __tablename__ = 'article_analysis'

    id = Column(Integer, primary_key=True, autoincrement=True)
    sentiment_id = Column(Integer, ForeignKey('sentiment_analysis.id'), nullable=False)
    title_score = Column(Integer)
    title_explanation = Column(Text)
    body_score = Column(Integer)
    body_explanation = Column(Text)
    created_at = Column(DateTime, default=func.now())

    def to_dict(self) -> Dict[str, Any]:
        """Convert article analysis to dictionary"""
        return {
            "id": self.id,
            "title_score": self.title_score,
            "title_explanation": self.title_explanation,
            "body_score": self.body_score,
            "body_explanation": self.body_explanation
        }


class PartyAnalysis(Base):
    """
    Model for party-specific sentiment analysis.
    """
    __tablename__ = 'parties_analysis'

    id = Column(Integer, primary_key=True, autoincrement=True)
    sentiment_id = Column(Integer, ForeignKey('sentiment_analysis.id'), nullable=False)
    name = Column(Text)
    score = Column(Text)
    explanation = Column(Text)

    def to_dict(self) -> Dict[str, Any]:
        """Convert party analysis to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "score": self.score,
            "explanation": self.explanation
        }


class PoliticianAnalysis(Base):
    """
    Model for politician-specific sentiment analysis.
    """
    __tablename__ = 'politicians_analysis'

    id = Column(Integer, primary_key=True, autoincrement=True)
    sentiment_id = Column(Integer, ForeignKey('sentiment_analysis.id'), nullable=False)
    name = Column(Text)
    score = Column(Text)
    explanation = Column(Text)

    def to_dict(self) -> Dict[str, Any]:
        """Convert politician analysis to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "score": self.score,
            "explanation": self.explanation
        }
