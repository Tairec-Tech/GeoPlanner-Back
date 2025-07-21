from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import AgendaItem
from schemas.agenda import AgendaCreate, AgendaResponse

router = APIRouter(prefix="/agenda", tags=["Agenda"])

@router.post("/", response_model=AgendaResponse)
def create_agenda_item(item: AgendaCreate, db: Session = Depends(get_db)):
    db_item = AgendaItem(
        user_id=1,  # TODO: usuario autenticado
        title=item.title,
        description=item.description,
        date=item.date
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.get("/", response_model=list[AgendaResponse])
def get_agenda(db: Session = Depends(get_db)):
    return db.query(AgendaItem).filter(AgendaItem.usuario_id == 1).all()