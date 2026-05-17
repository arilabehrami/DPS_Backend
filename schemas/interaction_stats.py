from pydantic import BaseModel


class InteractionStatsCreate(BaseModel):
    user_id: int
    total_messages: int