from fastapi import APIRouter

router = APIRouter(prefix="/persona-history", tags=["PersonaHistory"])


@router.get("/")
def get_history():
    return {"message": "Persona history working"}