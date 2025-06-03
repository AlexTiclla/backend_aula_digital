from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Nota
from ..schemas.nota import NotaCreate, NotaUpdate, NotaResponse
from ..dependencies.auth import get_current_admin, get_current_user

router = APIRouter(prefix="/api/v1/notas", tags=["notas"])

@router.post("/", response_model=NotaResponse)
async def crear_nota(nota: NotaCreate, db: Session = Depends(get_db), current_user=Depends(get_current_admin)):
    nuevo = Nota(**nota.dict())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.get("/", response_model=list[NotaResponse])
async def listar_notas(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(Nota).all()

@router.get("/estudiante/{estudiante_id}", response_model=list[NotaResponse])
async def listar_notas_por_estudiante(estudiante_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(Nota).filter(Nota.estudiante_id == estudiante_id).all()

@router.get("/curso_materia/{curso_materia_id}", response_model=list[NotaResponse])
async def listar_notas_por_curso_materia(curso_materia_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(Nota).filter(Nota.curso_materia_id == curso_materia_id).all()

@router.get("/estudiante/{estudiante_id}/curso_materia/{curso_materia_id}", response_model=list[NotaResponse])
async def listar_notas_por_estudiante_y_curso_materia(
    estudiante_id: int, 
    curso_materia_id: int, 
    db: Session = Depends(get_db), 
    current_user=Depends(get_current_user)
):
    return db.query(Nota).filter(
        Nota.estudiante_id == estudiante_id,
        Nota.curso_materia_id == curso_materia_id
    ).all()

@router.get("/{id}", response_model=NotaResponse)
async def obtener_nota(id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    obj = db.query(Nota).filter(Nota.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="No encontrado")
    return obj

@router.put("/{id}", response_model=NotaResponse)
async def actualizar_nota(id: int, data: NotaUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_admin)):
    obj = db.query(Nota).filter(Nota.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="No encontrado")
    for key, value in data.dict(exclude_unset=True).items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/{id}")
async def eliminar_nota(id: int, db: Session = Depends(get_db), current_user=Depends(get_current_admin)):
    obj = db.query(Nota).filter(Nota.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="No encontrado")
    db.delete(obj)
    db.commit()
    return {"message": "Eliminado"}
