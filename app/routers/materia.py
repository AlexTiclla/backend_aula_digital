from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Materia
from ..schemas.materia import MateriaCreate, MateriaUpdate, MateriaResponse
from ..dependencies.auth import get_current_admin

router = APIRouter(prefix="/api/v1/materias", tags=["materias"])

@router.post("/", response_model=MateriaResponse)
async def crear_materia(materia: MateriaCreate, db: Session = Depends(get_db), current_user=Depends(get_current_admin)):
    nuevo = Materia(**materia.dict())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.get("/", response_model=list[MateriaResponse])
async def listar_materias(db: Session = Depends(get_db)):
    return db.query(Materia).all()

@router.get("/{id}", response_model=MateriaResponse)
async def obtener_materia(id: int, db: Session = Depends(get_db)):
    obj = db.query(Materia).filter(Materia.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="No encontrado")
    return obj

@router.put("/{id}", response_model=MateriaResponse)
async def actualizar_materia(id: int, data: MateriaUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_admin)):
    obj = db.query(Materia).filter(Materia.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="No encontrado")
    for key, value in data.dict(exclude_unset=True).items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/{id}")
async def eliminar_materia(id: int, db: Session = Depends(get_db), current_user=Depends(get_current_admin)):
    obj = db.query(Materia).filter(Materia.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="No encontrado")
    db.delete(obj)
    db.commit()
    return {"message": "Eliminado"}
