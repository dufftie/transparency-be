import re
from contextlib import contextmanager
from typing import Any, Generic, List, Optional, Type, TypeVar

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session, Query
from unidecode import unidecode

from db.db_connector import DBConnector

# Generic type for models
T = TypeVar('T')
# Generic type for input schema
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
# Generic type for update schema
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)


def get_db_session():
    """
    Create a database connection and return a session
    """
    db = DBConnector()
    session = db.session
    return session


@contextmanager
def db_session():
    """
    Context manager for database sessions to ensure proper cleanup
    """
    session = get_db_session()
    try:
        yield session
    finally:
        session.close()


def get_db():
    """
    Dependency for FastAPI to inject db session
    """
    with db_session() as session:
        yield session


def check_results(results, detail="No data found for the given parameters"):
    """
    Check if results exist and raise HTTPException if not
    """
    if not results:
        raise HTTPException(status_code=404, detail=detail)
    return results


def slugify(text):
    """
    Convert text to a URL-friendly slug.
    
    Args:
        text (str): The text to convert to a slug
        
    Returns:
        str: A URL-friendly slug
    """
    # Convert to ASCII
    text = unidecode(text)
    # Convert to lowercase
    text = text.lower()
    # Remove non-alphanumeric characters and replace with hyphens
    text = re.sub(r'[^a-z0-9]+', '-', text)
    # Remove leading/trailing hyphens
    text = text.strip('-')
    return text


class FilterParams:
    """Base class for common filter parameters"""
    
    def __init__(
        self,
        media_id: Optional[int] = None,
        category: Optional[str] = None,
        paywall: Optional[bool] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ):
        self.media_id = media_id
        self.category = category
        self.paywall = paywall
        self.start_date = start_date
        self.end_date = end_date


class QueryBuilder:
    """Helper class to build common queries with filters"""
    
    @staticmethod
    def apply_filters(query: Query, article, filters: FilterParams) -> Query:
        """Apply common filters to a query"""
        if filters.media_id:
            query = query.filter(article.media_id == filters.media_id)
            
        if filters.category:
            query = query.filter(article.category == filters.category)
            
        if filters.paywall is not None:
            query = query.filter(article.paywall == filters.paywall)
            
        if filters.start_date:
            query = query.filter(article.date_time >= filters.start_date)
            
        if filters.end_date:
            query = query.filter(article.date_time <= filters.end_date)
            
        return query


class BaseRepository(Generic[T]):
    """
    Base repository with common database operations
    """
    
    def __init__(self, model: Type[T]):
        self.model = model
    
    def get(self, db: Session, id: Any) -> Optional[T]:
        """Get entity by ID"""
        return db.query(self.model).filter(self.model.id == id).first()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all entities with pagination"""
        return db.query(self.model).offset(skip).limit(limit).all()
    
    def create(self, db: Session, obj_in: CreateSchemaType) -> T:
        """Create new entity"""
        obj_in_data = obj_in.dict()
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(self, db: Session, db_obj: T, obj_in: UpdateSchemaType) -> T:
        """Update entity"""
        obj_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            setattr(db_obj, field, obj_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def remove(self, db: Session, id: Any) -> T:
        """Delete entity"""
        obj = db.query(self.model).get(id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj
    
    def filter_by(self, db: Session, **kwargs) -> List[T]:
        """Filter entities by given parameters"""
        return db.query(self.model).filter_by(**kwargs).all()
    
    def apply_filters(self, db: Session, filters: FilterParams) -> List[T]:
        """Apply common filters"""
        query = db.query(self.model)
        return QueryBuilder.apply_filters(query, self.model, filters).all()
