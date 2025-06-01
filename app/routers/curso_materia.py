from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import CursoMateria
from ..schemas.curso_materia import CursoMateriaCreate, CursoMateriaUpdate, CursoMateriaResponse
from ..dependencies.auth import get_current_admin

router = APIRouter(prefix="/api/v1/curso_materias", tags=["curso_materias"])

@router.post("/", response_model=CursoMateriaResponse)
async def crear_curso_materia(data: CursoMateriaCreate, db: Session = Depends(get_db), current_user=Depends(get_current_admin)):
    nuevo = CursoMateria(**data.dict())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.get("/", response_model=list[CursoMateriaResponse])
async def listar_curso_materias(db: Session = Depends(get_db)):
    return db.query(CursoMateria).all()

@router.get("/{id}", response_model=CursoMateriaResponse)
async def obtener_curso_materia(id: int, db: Session = Depends(get_db)):
    obj = db.query(CursoMateria).filter(CursoMateria.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="No encontrado")
    return obj

@router.put("/{id}", response_model=CursoMateriaResponse)
async def actualizar_curso_materia(id: int, data: CursoMateriaUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_admin)):
    obj = db.query(CursoMateria).filter(CursoMateria.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="No encontrado")
    for key, value in data.dict(exclude_unset=True).items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/{id}")
async def eliminar_curso_materia(id: int, db: Session = Depends(get_db), current_user=Depends(get_current_admin)):
    obj = db.query(CursoMateria).filter(CursoMateria.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="No encontrado")
    db.delete(obj)
    db.commit()
    return {"message": "Eliminado"}
