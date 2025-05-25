from itemadapter import ItemAdapter

from lib.crawler.helpers.utils import serialize_text_prop
from db.db_connector import DBConnector
from db.models.models import Article


class PostimeesPipeline:
    def process_item(self, item, spider):
        """Process each item and insert it into the database."""
        adapter = ItemAdapter(item)
        field_names = adapter.field_names()

        for field_name in field_names:
            value = adapter.get(field_name)
            if field_name == 'body':
                adapter[field_name] = serialize_text_prop(value)
            elif field_name in ['title', 'authors', 'category']:
                if isinstance(value, str):
                    adapter[field_name] = value.strip()
            elif field_name == 'paywall':
                adapter[field_name] = bool(value)
            elif field_name == 'date_time':
                if not value:
                    print("Article doesn't have a date_time field")
                    return None

        article = Article(**item)
        db = DBConnector()
        db.insert_or_update_article(article)
        return item
