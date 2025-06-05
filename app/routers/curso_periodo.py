from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session,joinedload

from app.schemas.users import EstudianteResponse
from ..database import get_db
from ..models import Curso, CursoMateria, CursoPeriodo, Estudiante, Nota, Pertenece
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

from sqlalchemy.orm import joinedload
from sqlalchemy import select
from sqlalchemy.orm import aliased
from app.models import CursoPeriodo, Curso, Periodo

@router.get("/get", response_model=List[CursoPeriodoResponse])
def get_curso_periodos(db: Session = Depends(get_db)):
    results = (
        db.query(
            CursoPeriodo.id,
            CursoPeriodo.curso_id,
            Curso.nombre.label("curso_nombre"),
            CursoPeriodo.periodo_id,
            Periodo.descripcion.label("periodo_nombre"),  # ✅ AÑADIR ESTO
            CursoPeriodo.aula,
            CursoPeriodo.turno,
            CursoPeriodo.capacidad_actual,
            CursoPeriodo.is_active
        )
        .join(Curso)
        .join(Periodo)
        .all()
    )

    return [
        CursoPeriodoResponse(
            id=r.id,
            curso_id=r.curso_id,
            curso_nombre=r.curso_nombre,
            periodo_id=r.periodo_id,
            periodo_nombre=r.periodo_nombre,
            aula=r.aula,
            turno=r.turno,
            capacidad_actual=r.capacidad_actual,
            is_active=r.is_active
        )
        for r in results
    ]


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

@router.get("/curso_periodo/{id}/estudiantes", response_model=List[EstudianteResponse])
async def obtener_estudiantes_por_curso_periodo(id: int, db: Session = Depends(get_db)):
    """
    Obtener todos los estudiantes inscritos en un curso_periodo dado su ID.
    """
    # Paso 1: Obtener los curso_materia del curso_periodo
    curso_materia_ids = db.query(CursoMateria.id).filter(
        CursoMateria.curso_periodo_id == id
    ).all()
    curso_materia_ids = [cm[0] for cm in curso_materia_ids]

    if not curso_materia_ids:
        return []

    # Paso 2: Obtener inscripciones desde la tabla pertenece
    estudiante_ids = db.query(Pertenece.estudiante_id).filter(
        Pertenece.curso_materia_id.in_(curso_materia_ids)
    ).distinct().all()
    estudiante_ids = [e[0] for e in estudiante_ids]

    if not estudiante_ids:
        return []

    # Paso 3: Obtener los estudiantes con sus relaciones
    estudiantes = db.query(Estudiante).filter(
        Estudiante.id.in_(estudiante_ids)
    ).options(
        joinedload(Estudiante.usuario),
        joinedload(Estudiante.tutor)
    ).all()

    return estudiantes


@router.get("/curso_materia/{curso_materia_id}/estudiantes", response_model=List[EstudianteResponse])
async def obtener_estudiantes_por_curso_materia(curso_materia_id: int, db: Session = Depends(get_db)):
    estudiante_ids = db.query(Nota.estudiante_id).filter(Nota.curso_materia_id == curso_materia_id).distinct()
    estudiantes = db.query(Estudiante).filter(Estudiante.id.in_(estudiante_ids)).options(
        joinedload(Estudiante.usuario),
        joinedload(Estudiante.tutor)
    ).all()
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
