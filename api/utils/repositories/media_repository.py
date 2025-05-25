from api.utils.db_utils import BaseRepository
from db.models.models import Media


class MediaRepository(BaseRepository[Media]):
    """Repository for handling Media operations"""
    
    def __init__(self):
        super().__init__(Media)