from unicodedata import category

from sqlalchemy import desc

from db.db_connector import DBConnector
from db.models.models import Article
from lib.sentiment.analyzers.gemini import GeminiSentimentModel

db = DBConnector()
session = db.session

# MEDIA ANALYSIS
media_id = 2
categories = [
    'Arvamus',
    'Eesti',
    'Majandus',
    # 'Postimees',
    'Tallinn'
]
model = GeminiSentimentModel(media_id)

articles = (
    session
    .query(Article)
    .filter_by(media_id=media_id, paywall=False)
    .filter(Article.date_time.isnot(None))
    .order_by(desc(Article.date_time))
    .all()
)

print("Articles to analyze:", len(articles))
sentiments = model.analyze(articles)
