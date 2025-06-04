from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session,joinedload

from app.schemas.users import EstudianteResponse
from ..database import get_db
from ..models import CursoPeriodo, Estudiante
from ..schemas.curso_periodo import CursoPeriodoCreate, CursoPeriodoUpdate, CursoPeriodoResponse
from ..dependencies.auth import get_current_admin

router = APIRouter(prefix="/api/v1/curso_periodos", tags=["curso_periodos"])

@router.get("/", response_model=List[CursoPeriodoResponse])
async def get_curso_periodos(db: Session = Depends(get_db)):
    curso_periodos = db.query(CursoPeriodo).options(
        joinedload(CursoPeriodo.curso),
        joinedload(CursoPeriodo.periodo)
    ).all()

    result = []
    for cp in curso_periodos:
        result.append({
            "id": cp.id,
            "curso_id": cp.curso_id,
            "curso_nombre": cp.curso.nombre if cp.curso else None,
            "periodo_id": cp.periodo_id,
            "periodo_nombre": cp.periodo.descripcion if cp.periodo else None,
            "aula": cp.aula,
            "turno": cp.turno,
            "capacidad_actual": cp.capacidad_actual,
            "is_active": cp.is_active
        })
    return result

@router.get("/", response_model=list[CursoPeriodoResponse])
async def listar_curso_periodos(db: Session = Depends(get_db)):
    return db.query(CursoPeriodo).all()

@router.get("/{id}", response_model=CursoPeriodoResponse)
async def obtener_curso_periodo(id: int, db: Session = Depends(get_db)):
    obj = db.query(CursoPeriodo).filter(CursoPeriodo.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="No encontrado")
    return obj


@router.get("/{id}/estudiantes", response_model=List[EstudianteResponse])
async def obtener_estudiantes_por_curso_periodo(id: int, db: Session = Depends(get_db)):
    estudiantes = db.query(Estudiante).options(
        joinedload(Estudiante.usuario),
        joinedload(Estudiante.tutor),
        joinedload(Estudiante.curso_periodo).joinedload(CursoPeriodo.curso)
    ).filter(Estudiante.curso_periodo_id == id).all()
    return estudiantes


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
