from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.curso import Curso
from ..schemas.curso import CursoCreate, CursoUpdate, CursoResponse
from ..dependencies.auth import get_current_admin

router = APIRouter(prefix="/api/v1/cursos", tags=["cursos"])

@router.post("/", response_model=CursoResponse)
async def crear_curso(curso: CursoCreate, db: Session = Depends(get_db), current_user=Depends(get_current_admin)):
    nuevo_curso = Curso(**curso.dict())
    db.add(nuevo_curso)
    db.commit()
    db.refresh(nuevo_curso)
    return nuevo_curso

@router.get("/", response_model=list[CursoResponse])
async def listar_cursos(db: Session = Depends(get_db)):
    return db.query(Curso).all()

@router.get("/{curso_id}", response_model=CursoResponse)
async def obtener_curso(curso_id: int, db: Session = Depends(get_db)):
    curso = db.query(Curso).filter(Curso.id == curso_id).first()
    if not curso:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    return curso

@router.put("/{curso_id}", response_model=CursoResponse)
async def actualizar_curso(curso_id: int, curso_data: CursoUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_admin)):
    curso = db.query(Curso).filter(Curso.id == curso_id).first()
    if not curso:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    for key, value in curso_data.dict(exclude_unset=True).items():
        setattr(curso, key, value)
    db.commit()
    db.refresh(curso)
    return curso

@router.delete("/{curso_id}")
async def eliminar_curso(curso_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_admin)):
    curso = db.query(Curso).filter(Curso.id == curso_id).first()
    if not curso:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    db.delete(curso)
    db.commit()
    return {"message": "Curso eliminado"}
