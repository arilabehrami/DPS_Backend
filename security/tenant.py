from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.conversation import Conversation
from models.feedback import Feedback
from models.message import Message
from models.notification import Notification
from models.persona import Persona
from models.persona_history import PersonaHistory
from models.persona_trait import PersonaTrait
from models.personality import Personality
from models.settings import Settings
from models.user import User


def ensure_workspace_access(resource_workspace_id: int, current_user: User) -> None:
    if resource_workspace_id != current_user.workspace_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Resource does not belong to your workspace",
        )


def ensure_user_access(db: Session, user_id: int, current_user: User) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    ensure_workspace_access(user.workspace_id, current_user)
    return user


def ensure_persona_access(db: Session, persona_id: int, current_user: User) -> Persona:
    persona = db.query(Persona).filter(Persona.id == persona_id).first()
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")

    ensure_workspace_access(persona.workspace_id, current_user)
    return persona


def ensure_personality_access(
    db: Session, personality_id: int, current_user: User
) -> Personality:
    personality = db.query(Personality).filter(Personality.id == personality_id).first()
    if not personality:
        raise HTTPException(status_code=404, detail="Personality not found")

    ensure_workspace_access(personality.workspace_id, current_user)
    return personality


def ensure_conversation_access(
    db: Session, conversation_id: int, current_user: User
) -> Conversation:
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    ensure_workspace_access(conversation.workspace_id, current_user)
    return conversation


def ensure_message_access(db: Session, message_id: int, current_user: User) -> Message:
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    ensure_workspace_access(message.workspace_id, current_user)
    return message


def ensure_persona_trait_access(
    db: Session, trait_id: int, current_user: User
) -> PersonaTrait:
    trait = db.query(PersonaTrait).filter(PersonaTrait.id == trait_id).first()
    if not trait:
        raise HTTPException(status_code=404, detail="Persona trait not found")

    if trait.persona_id is not None:
        ensure_persona_access(db, trait.persona_id, current_user)
    return trait


def ensure_persona_history_access(
    db: Session, history_id: int, current_user: User
) -> PersonaHistory:
    history = db.query(PersonaHistory).filter(PersonaHistory.id == history_id).first()
    if not history:
        raise HTTPException(status_code=404, detail="Persona history not found")

    ensure_persona_access(db, history.persona_id, current_user)
    return history


def ensure_feedback_access(db: Session, feedback_id: int, current_user: User) -> Feedback:
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")

    ensure_user_access(db, feedback.user_id, current_user)
    return feedback


def ensure_notification_access(
    db: Session, notification_id: int, current_user: User
) -> Notification:
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    if notification.user_id is not None:
        ensure_user_access(db, notification.user_id, current_user)
    return notification


def ensure_settings_access(db: Session, settings_id: int, current_user: User) -> Settings:
    settings = db.query(Settings).filter(Settings.id == settings_id).first()
    if not settings:
        raise HTTPException(status_code=404, detail="Settings not found")

    if settings.user_id is not None:
        ensure_user_access(db, settings.user_id, current_user)
    return settings
