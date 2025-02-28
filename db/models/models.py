from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime, Boolean, String, Date, func, JSON, UniqueConstraint, \
    ForeignKeyConstraint
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Article(Base):
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

    __table_args__ = (
        UniqueConstraint('article_id', 'media_id', name='uq_article_media'),
    )


class Media(Base):
    __tablename__ = 'medias'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    base_url = Column(String(255), nullable=False)
    description = Column(Text)
    chief_editor_id = Column(Integer, ForeignKey('chief_editor_history.id'))


class Politicians(Base):
    __tablename__ = 'politicians'
    id = Column(Integer, primary_key=True, autoincrement=True)
    personal_id = Column(Integer)
    title = Column(String(255), nullable=False)
    aliases = Column(Text)
    current_party = Column(Integer, ForeignKey('parties.id'))

class Parties(Base):
    __tablename__ = 'parties'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    aliases = Column(Text)


class ChiefEditorHistory(Base):
    __tablename__ = 'chief_editor_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    media_id = Column(Integer, ForeignKey('medias.id'), nullable=False)
    chief_editor = Column(String(255), nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)


class SentimentAnalysis(Base):
    __tablename__ = 'sentiment_analysis'
    id = Column(Integer, primary_key=True, autoincrement=True)
    media_id = Column(Integer, nullable=False)
    article_id = Column(Integer, nullable=False)
    model = Column(String(25), nullable=False)
    sentiment = Column(JSON, nullable=False)

    # Composite foreign key referencing article_id and media_id
    __table_args__ = (
        ForeignKeyConstraint(
            ['article_id', 'media_id'],
            ['articles.article_id', 'articles.media_id'],
            name='fk_sentiment_article'
        ),
        UniqueConstraint('article_id', 'media_id', 'model', name='uq_article_media_model')
    )


class ArticleAnalysis(Base):
    __tablename__ = 'article_analysis'

    id = Column(Integer, primary_key=True, autoincrement=True)
    sentiment_id = Column(Integer, ForeignKey('sentiment_analysis.id'), nullable=False)
    title_score = Column(Integer)
    title_explanation = Column(Text)
    body_score = Column(Integer)
    body_explanation = Column(Text)
    created_at = Column(DateTime, default=func.now())


class PartyAnalysis(Base):
    __tablename__ = 'parties_analysis'

    id = Column(Integer, primary_key=True, autoincrement=True)
    sentiment_id = Column(Integer, ForeignKey('sentiment_analysis.id'), nullable=False)
    name = Column(Text)
    score = Column(Text)
    explanation = Column(Text)


class PoliticianAnalysis(Base):
    __tablename__ = 'politicians_analysis'

    id = Column(Integer, primary_key=True, autoincrement=True)
    sentiment_id = Column(Integer, ForeignKey('sentiment_analysis.id'), nullable=False)
    name = Column(Text)
    score = Column(Text)
    explanation = Column(Text)
