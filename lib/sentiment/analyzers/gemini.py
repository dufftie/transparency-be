import os

import google.generativeai as genai
from dotenv import load_dotenv
from google.ai.generativelanguage_v1beta.types import content

from lib.sentiment.analyzers.sentiment_base_analyzer import SentimentBaseAnalyzer
from lib.sentiment.analyzers.prompts.article_analysis_prompt_ru import article_analysis_prompt_ru
from lib.sentiment.analyzers.prompts.article_analysis_prompt_ee import article_analysis_prompt_ee

generation_config = {
    "temperature": 0.5,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_schema": content.Schema(
        type=content.Type.OBJECT,
        enum=[],
        required=["article", "parties", "politicians"],
        properties={
            "article": content.Schema(
                type=content.Type.OBJECT,
                enum=[],
                required=["title", "body"],
                properties={
                    "title": content.Schema(
                        type=content.Type.OBJECT,
                        enum=[],
                        required=["score", "explanation"],
                        properties={
                            "score": content.Schema(
                                type=content.Type.NUMBER,
                            ),
                            "explanation": content.Schema(
                                type=content.Type.STRING,
                            ),
                        },
                    ),
                    "body": content.Schema(
                        type=content.Type.OBJECT,
                        enum=[],
                        required=["score", "explanation"],
                        properties={
                            "score": content.Schema(
                                type=content.Type.INTEGER,
                            ),
                            "explanation": content.Schema(
                                type=content.Type.STRING,
                            ),
                        },
                    ),
                },
            ),
            "parties": content.Schema(
                type=content.Type.ARRAY,
                items=content.Schema(
                    type=content.Type.OBJECT,
                    enum=[],
                    required=["name", "score", "explanation"],
                    properties={
                        "name": content.Schema(
                            type=content.Type.STRING,
                        ),
                        "score": content.Schema(
                            type=content.Type.INTEGER,
                        ),
                        "explanation": content.Schema(
                            type=content.Type.STRING,
                        ),
                    },
                ),
            ),
            "politicians": content.Schema(
                type=content.Type.ARRAY,
                items=content.Schema(
                    type=content.Type.OBJECT,
                    enum=[],
                    required=["name", "score", "explanation"],
                    properties={
                        "name": content.Schema(
                            type=content.Type.STRING,
                        ),
                        "score": content.Schema(
                            type=content.Type.INTEGER,
                        ),
                        "explanation": content.Schema(
                            type=content.Type.STRING,
                        ),
                    },
                ),
            ),
        },
    ),
    "response_mime_type": "application/json",
}


class GeminiSentimentModel(SentimentBaseAnalyzer):
    """Google Gemini interface specific model"""

    # noinspection PyTypeChecker
    def __init__(self, media_id: int):
        self.model_name = "gemini-2.0-flash"
        super().__init__(self.model_name)

        load_dotenv()
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

        if media_id == 1:
            system_instruction = article_analysis_prompt_ru
        elif media_id == 2:
            system_instruction = article_analysis_prompt_ee

        if not system_instruction: raise Exception("No system prompt found! Aborting the analysis")

        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=generation_config,
            system_instruction=system_instruction,
        )
        self.chat_session = self.model.start_chat()

    def send_message(self, text: str):
        response = self.chat_session.send_message(text)
        return response.text
