from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Curso, CursoMateria
from ..schemas.curso import CursoCreate, CursoDetailResponse, CursoUpdate, CursoResponse
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

@router.get("/detallado", response_model=List[CursoDetailResponse])
async def listar_cursos_detallado(db: Session = Depends(get_db)):
    cursos = db.query(Curso).all()
    curso_detalles = []
    
    for curso in cursos:
        # Contar estudiantes inscritos (puedes ajustar según tu modelo)
        capacidad_actual = db.query(CursoMateria).filter(CursoMateria.curso_periodo.has(curso_id=curso.id)).count()
        
        # Obtener información del profesor, si existe
        curso_materia = db.query(CursoMateria).filter(CursoMateria.curso_periodo.has(curso_id=curso.id)).first()
        profesor_nombre = None
        horario = None
        aula = None
        if curso_materia:
            if curso_materia.profesor:
                profesor_nombre = curso_materia.profesor.usuario.nombre
            horario = curso_materia.horario
            aula = curso_materia.aula
        
        curso_detalles.append(CursoDetailResponse(
            id=curso.id,
            nombre=curso.nombre,
            sigla=curso.sigla,
            nivel=curso.nivel,
            capacidad_maxima=curso.capacidad_maxima,
            descripcion=curso.descripcion,
            is_active=curso.is_active,
            capacidad_actual=capacidad_actual,
            profesor=profesor_nombre,
            horario=horario,
            aula=aula
        ))

    return curso_detalles


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

