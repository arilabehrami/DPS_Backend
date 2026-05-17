from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.persona import Persona
from schemas.persona import PersonaCreate, PersonaResponse

router = APIRouter(
    prefix="/personas",
    tags=["Personas"]
)


@router.post("/", response_model=PersonaResponse)
def create_persona(
    persona_data: PersonaCreate,
    db: Session = Depends(get_db)
):
    persona = Persona(**persona_data.model_dump())

    db.add(persona)
    db.commit()
    db.refresh(persona)

    return persona


@router.get("/", response_model=list[PersonaResponse])
def get_personas(db: Session = Depends(get_db)):
    return db.query(Persona).all()