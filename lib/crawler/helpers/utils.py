import re


def clean_text(text):
    cleaned_text = re.sub(r'[\xa0\u200b]', ' ', text)  # Replace NBSP and Zero Width Space with a space
    cleaned_text = re.sub(r'&[a-zA-Z]+;', '', cleaned_text)  # Remove HTML entities like &amp;, &lt;, etc.
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)  # Normalize whitespace to a single space
    return cleaned_text.strip()


def serialize_text_prop(value):
    return clean_text(" ".join(value)).strip()


def format_article_request(media_id, title, body):
    if media_id == 1:
        return f"""
                ЗАГОЛОВОК: {title}

                ТЕКСТ СТАТЬИ:
                {body}
            """
    if media_id == 2:
        return f"""
                    PEALKIRI: {title}
    
                    ARTIKLI TEKST:
                    {body}
                """

    raise Exception("No media_id provided for format_article_request")
