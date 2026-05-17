from fastapi import APIRouter

router = APIRouter(prefix="/prompt-templates", tags=["PromptTemplate"])


@router.get("/")
def get_templates():
    return {"message": "Prompt templates working"}