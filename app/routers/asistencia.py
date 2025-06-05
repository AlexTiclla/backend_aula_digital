from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import Asistencia, CursoPeriodo, Estudiante, CursoMateria
from ..schemas.asistencia import Asistencia as AsistenciaSchema, AsistenciaConPeriodoResponse, AsistenciaCreate, AsistenciaUpdate
from ..dependencies.auth import get_current_user

router = APIRouter(
    prefix="/asistencias",
    tags=["asistencias"],
    responses={404: {"description": "No encontrado"}},
)

@router.post("/", response_model=AsistenciaSchema, status_code=status.HTTP_201_CREATED)
def create_asistencia(asistencia: AsistenciaCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # Verificar si el estudiante existe
    estudiante = db.query(Estudiante).filter(Estudiante.id == asistencia.estudiante_id).first()
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    
    # Verificar si el curso_materia existe
    curso_materia = db.query(CursoMateria).filter(CursoMateria.id == asistencia.curso_materia_id).first()
    if not curso_materia:
        raise HTTPException(status_code=404, detail="Curso materia no encontrado")
    
    db_asistencia = Asistencia(**asistencia.dict())
    db.add(db_asistencia)
    db.commit()
    db.refresh(db_asistencia)
    return db_asistencia

@router.get("/", response_model=List[AsistenciaSchema])
def read_asistencias(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    asistencias = db.query(Asistencia).offset(skip).limit(limit).all()
    return asistencias

@router.get("/{asistencia_id}", response_model=AsistenciaSchema)
def read_asistencia(asistencia_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    asistencia = db.query(Asistencia).filter(Asistencia.id == asistencia_id).first()
    if asistencia is None:
        raise HTTPException(status_code=404, detail="Asistencia no encontrada")
    return asistencia

@router.get("/estudiante/{estudiante_id}", response_model=List[AsistenciaSchema])
def read_asistencias_by_estudiante(estudiante_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    asistencias = db.query(Asistencia).filter(Asistencia.estudiante_id == estudiante_id).all()
    return asistencias

@router.get("/curso_materia/{curso_materia_id}", response_model=List[AsistenciaSchema])
def read_asistencias_by_curso_materia(curso_materia_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    asistencias = db.query(Asistencia).filter(Asistencia.curso_materia_id == curso_materia_id).all()
    return asistencias

@router.put("/{asistencia_id}", response_model=AsistenciaSchema)
def update_asistencia(asistencia_id: int, asistencia: AsistenciaUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    db_asistencia = db.query(Asistencia).filter(Asistencia.id == asistencia_id).first()
    if db_asistencia is None:
        raise HTTPException(status_code=404, detail="Asistencia no encontrada")
    
    update_data = asistencia.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_asistencia, key, value)
    
@router.get("/estudiante/{estudiante_id}/curso_materia/{curso_materia_id}", response_model=List[AsistenciaSchema])
def read_asistencias_by_estudiante_and_curso_materia(
    estudiante_id: int,
    curso_materia_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    asistencias = db.query(Asistencia).filter(
        Asistencia.estudiante_id == estudiante_id,
        Asistencia.curso_materia_id == curso_materia_id
    ).all()
    
    return asistencias        

from sqlalchemy.orm import joinedload

@router.get("/estudiante/{estudiante_id}/materia/{materia_id}/asistencias", response_model=List[AsistenciaConPeriodoResponse])
def read_asistencias_by_materia_with_periodo(
    estudiante_id: int,
    materia_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    estudiante = db.query(Estudiante).filter_by(id=estudiante_id).first()
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")

    curso_materia_ids = db.query(CursoMateria.id).filter_by(materia_id=materia_id).all()
    curso_materia_ids = [cm[0] for cm in curso_materia_ids]

    if not curso_materia_ids:
        return []

    asistencias = db.query(Asistencia).filter(
        Asistencia.estudiante_id == estudiante_id,
        Asistencia.curso_materia_id.in_(curso_materia_ids)
    ).options(
        joinedload(Asistencia.curso_materia)
        .joinedload(CursoMateria.curso_periodo)
        .joinedload(CursoPeriodo.periodo)
    ).all()

    resultado = []
    for a in asistencias:
        periodo = a.curso_materia.curso_periodo.periodo
        resultado.append({
            "id": a.id,
            "estudiante_id": a.estudiante_id,
            "curso_materia_id": a.curso_materia_id,
            "valor": a.valor,
            "fecha": a.fecha,
            "periodo": {
                "bimestre": periodo.bimestre,
                "anio": periodo.anio,
                "descripcion": periodo.descripcion
            }
        })

    return resultado


@router.delete("/{asistencia_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asistencia(asistencia_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    db_asistencia = db.query(Asistencia).filter(Asistencia.id == asistencia_id).first()
    if db_asistencia is None:
        raise HTTPException(status_code=404, detail="Asistencia no encontrada")
    
    db.delete(db_asistencia)
    db.commit()
    return None

