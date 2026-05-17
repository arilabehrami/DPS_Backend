from pydantic import BaseModel


class FeedbackCreate(BaseModel):
    user_id: int
    message: str
    rating: int


class FeedbackOut(BaseModel):
    id: int
    user_id: int
    message: str
    rating: int

    class Config:
        from_attributes = True