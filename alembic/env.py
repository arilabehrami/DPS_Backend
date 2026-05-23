from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

from database import Base  
from models.ai_response import AIResponse
from models.api_key import APIKey
from models.audit_log import AuditLog
from models.chat_message import ChatMessage
from models.conversation import Conversation
from models.event_log import EventLog
from models.feedback import Feedback
from models.interaction_stats import InteractionStats
from models.message import Message
from models.notification import Notification
from models.persona import Persona
from models.persona_history import PersonaHistory
from models.persona_trait import PersonaTrait
from models.personality import Personality
from models.prompt_template import PromptTemplate
from models.role import Role
from models.session import Session
from models.settings import Settings
from models.user import User
from models.workspace import Workspace



config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
