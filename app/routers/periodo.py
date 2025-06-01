from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.periodo import Periodo
from ..schemas.periodo import PeriodoCreate, PeriodoUpdate, PeriodoResponse
from ..dependencies.auth import get_current_admin

router = APIRouter(prefix="/api/v1/periodos", tags=["periodos"])

@router.post("/", response_model=PeriodoResponse)
async def crear_periodo(periodo: PeriodoCreate, db: Session = Depends(get_db), current_user=Depends(get_current_admin)):
    nuevo = Periodo(**periodo.dict())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.get("/", response_model=list[PeriodoResponse])
async def listar_periodos(db: Session = Depends(get_db)):
    return db.query(Periodo).all()

@router.get("/{id}", response_model=PeriodoResponse)
async def obtener_periodo(id: int, db: Session = Depends(get_db)):
    obj = db.query(Periodo).filter(Periodo.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="No encontrado")
    return obj

@router.put("/{id}", response_model=PeriodoResponse)
async def actualizar_periodo(id: int, data: PeriodoUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_admin)):
    obj = db.query(Periodo).filter(Periodo.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="No encontrado")
    for key, value in data.dict(exclude_unset=True).items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/{id}")
async def eliminar_periodo(id: int, db: Session = Depends(get_db), current_user=Depends(get_current_admin)):
    obj = db.query(Periodo).filter(Periodo.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="No encontrado")
    db.delete(obj)
    db.commit()
    return {"message": "Eliminado"}
