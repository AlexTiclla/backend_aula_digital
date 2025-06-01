from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.curso_periodo import CursoPeriodo
from ..schemas.curso_periodo import CursoPeriodoCreate, CursoPeriodoUpdate, CursoPeriodoResponse
from ..dependencies.auth import get_current_admin

router = APIRouter(prefix="/api/v1/curso_periodos", tags=["curso_periodos"])

@router.post("/", response_model=CursoPeriodoResponse)
async def crear_curso_periodo(curso_periodo: CursoPeriodoCreate, db: Session = Depends(get_db), current_user=Depends(get_current_admin)):
    nuevo = CursoPeriodo(**curso_periodo.dict())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.get("/", response_model=list[CursoPeriodoResponse])
async def listar_curso_periodos(db: Session = Depends(get_db)):
    return db.query(CursoPeriodo).all()

@router.get("/{id}", response_model=CursoPeriodoResponse)
async def obtener_curso_periodo(id: int, db: Session = Depends(get_db)):
    obj = db.query(CursoPeriodo).filter(CursoPeriodo.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="No encontrado")
    return obj

@router.put("/{id}", response_model=CursoPeriodoResponse)
async def actualizar_curso_periodo(id: int, data: CursoPeriodoUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_admin)):
    obj = db.query(CursoPeriodo).filter(CursoPeriodo.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="No encontrado")
    for key, value in data.dict(exclude_unset=True).items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/{id}")
async def eliminar_curso_periodo(id: int, db: Session = Depends(get_db), current_user=Depends(get_current_admin)):
    obj = db.query(CursoPeriodo).filter(CursoPeriodo.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="No encontrado")
    db.delete(obj)
    db.commit()
    return {"message": "Eliminado"}
