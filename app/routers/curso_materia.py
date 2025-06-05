from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.schemas.users import EstudianteResponse
from ..database import get_db
from ..models import CursoMateria, CursoPeriodo, Estudiante, Materia, Pertenece
from ..schemas.curso_materia import CursoMateriaCreate, CursoMateriaEstudiantesResumen, CursoMateriaPorPeriodoResponse, CursoMateriaUpdate, CursoMateriaResponse
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

@router.get("/resumen-estudiantes", response_model=List[CursoMateriaEstudiantesResumen])
def resumen_estudiantes_por_curso_materia(db: Session = Depends(get_db)):
    curso_materias = db.query(CursoMateria).all()

    resumen = []
    for cm in curso_materias:
        cantidad = db.query(Pertenece).filter(Pertenece.curso_materia_id == cm.id).count()
        nombre_materia = cm.materia.nombre if cm.materia else f"ID {cm.materia_id}"
        resumen.append({
            "curso_materia_id": cm.id,
            "nombre_materia": nombre_materia,
            "cantidad_estudiantes": cantidad
        })

    return resumen

@router.get("/{id}", response_model=CursoMateriaResponse)
async def obtener_curso_materia(id: int, db: Session = Depends(get_db)):
    obj = db.query(CursoMateria).filter(CursoMateria.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="No encontrado")
    return obj



@router.get("/curso_materia/{id}/estudiantes", response_model=List[EstudianteResponse])
async def obtener_estudiantes_por_curso_materia(id: int, db: Session = Depends(get_db)):
    """
    Obtener todos los estudiantes inscritos en un curso_materia dado su ID.
    """
    inscripciones = db.query(Pertenece).filter(Pertenece.curso_materia_id == id).all()

    if not inscripciones:
        return []

    estudiante_ids = [insc.estudiante_id for insc in inscripciones]

    estudiantes = db.query(Estudiante).filter(Estudiante.id.in_(estudiante_ids)).options(
        joinedload(Estudiante.usuario),
        joinedload(Estudiante.tutor)
    ).all()

    return estudiantes


@router.get("/por_periodo/{periodo_id}", response_model=list[CursoMateriaPorPeriodoResponse])
def get_curso_materias_por_periodo(periodo_id: int, db: Session = Depends(get_db)):
    curso_materias = (
        db.query(CursoMateria)
        .join(CursoPeriodo)
        .join(Materia)
        .filter(CursoPeriodo.periodo_id == periodo_id)
        .all()
    )
    
    return [
        {
            "id": cm.id,
            "nombre_materia": cm.materia.nombre,
            "curso_periodo_id": cm.curso_periodo_id
        }
        for cm in curso_materias
    ]


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



