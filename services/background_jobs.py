from database import SessionLocal
from models.ai_response import AIResponse
from models.message import Message
from models.notification import Notification
from services.cache_service import invalidate_cache_prefix
from services.ollama_service import generate_with_ollama


def generate_ai_response_job(
    user_id: int,
    workspace_id: int,
    conversation_id: int,
    user_message_id: int,
    prompt: str,
    model: str | None = None,
) -> None:
    db = SessionLocal()

    try:
        response_text, model_used = generate_with_ollama(prompt, model)

        ai_message = Message(
            workspace_id=workspace_id,
            conversation_id=conversation_id,
            sender="ai",
            content=response_text,
        )
        db.add(ai_message)
        db.commit()
        db.refresh(ai_message)

        ai_response = AIResponse(
            message_id=user_message_id,
            response_text=response_text,
            model_used=model_used,
        )
        db.add(ai_response)

        notification = Notification(
            user_id=user_id,
            title="AI response generated successfully",
            is_read=False,
        )
        db.add(notification)
        db.commit()

        invalidate_cache_prefix("messages:")
    except Exception:
        db.rollback()

        notification = Notification(
            user_id=user_id,
            title="AI response generation failed",
            is_read=False,
        )
        db.add(notification)
        db.commit()
    finally:
        db.close()
