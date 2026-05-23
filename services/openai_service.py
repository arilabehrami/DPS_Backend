import logging
import os

from dotenv import load_dotenv
from fastapi import HTTPException, status
from openai import OpenAI, OpenAIError

load_dotenv()

logger = logging.getLogger("openai_service")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

if not OPENAI_API_KEY:
    logger.warning("OPENAI_API_KEY is missing")

client = OpenAI(api_key=OPENAI_API_KEY)


def chat_with_openai(message: str, model: str | None = None) -> str:
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY is missing")

    try:
        response = client.chat.completions.create(
            model=model or OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful AI chatbot."},
                {"role": "user", "content": message},
            ],
            temperature=0.7,
        )

        content = response.choices[0].message.content

        if not content:
            raise HTTPException(status_code=502, detail="OpenAI returned empty response")

        return content.strip()

    except OpenAIError as exc:
        logger.exception("OpenAI chat request failed")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc


def analyze_text_with_openai(text: str, model: str | None = None) -> str:
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY is missing")

    try:
        response = client.chat.completions.create(
            model=model or OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "Analyze this text. Return summary, sentiment, tone, and key points.",
                },
                {"role": "user", "content": text},
            ],
            temperature=0.3,
        )

        content = response.choices[0].message.content

        if not content:
            raise HTTPException(status_code=502, detail="OpenAI returned empty response")

        return content.strip()

    except OpenAIError as exc:
        logger.exception("OpenAI analyze request failed")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc