from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List

from ..database import get_db
from ..models import CursoPeriodo, Participaciones, Estudiante, CursoMateria
from ..schemas.participacion import Participacion, ParticipacionConPeriodoResponse, ParticipacionCreate, ParticipacionResponse, ParticipacionUpdate
from ..dependencies.auth import get_current_user

router = APIRouter(
    prefix="/api/v1/participaciones",
    tags=["participaciones"],
    responses={404: {"description": "No encontrado"}},
)

@router.post("/", response_model=Participacion, status_code=status.HTTP_201_CREATED)
def create_participacion(participacion: ParticipacionCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # Verificar si el estudiante existe
    estudiante = db.query(Estudiante).filter(Estudiante.id == participacion.estudiante_id).first()
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    
    # Verificar si el curso_materia existe
    curso_materia = db.query(CursoMateria).filter(CursoMateria.id == participacion.curso_materia_id).first()
    if not curso_materia:
        raise HTTPException(status_code=404, detail="Curso materia no encontrado")
    
    db_participacion = Participaciones(**participacion.dict())
    db.add(db_participacion)
    db.commit()
    db.refresh(db_participacion)
    return db_participacion

@router.get("/", response_model=List[Participacion])
def read_participaciones(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    participaciones = db.query(Participaciones).offset(skip).limit(limit).all()
    return participaciones

@router.get("/{participacion_id}", response_model=Participacion)
def read_participacion(participacion_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    participacion = db.query(Participaciones).filter(Participaciones.id == participacion_id).first()
    if participacion is None:
        raise HTTPException(status_code=404, detail="Participación no encontrada")
    return participacion

@router.get("/estudiante/{estudiante_id}", response_model=List[Participacion])
def read_participaciones_by_estudiante(estudiante_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    participaciones = db.query(Participaciones).filter(Participaciones.estudiante_id == estudiante_id).all()
    return participaciones

@router.get("/curso_materia/{curso_materia_id}", response_model=List[Participacion])
def read_participaciones_by_curso_materia(curso_materia_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    participaciones = db.query(Participaciones).filter(Participaciones.curso_materia_id == curso_materia_id).all()
    return participaciones

@router.put("/{participacion_id}", response_model=Participacion)
def update_participacion(participacion_id: int, participacion: ParticipacionUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    db_participacion = db.query(Participaciones).filter(Participaciones.id == participacion_id).first()
    if db_participacion is None:
        raise HTTPException(status_code=404, detail="Participación no encontrada")
    
    update_data = participacion.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_participacion, key, value)
        
    db.add(db_participacion)
    db.commit()
    db.refresh(db_participacion)
    return db_participacion


@router.get("/estudiante/{estudiante_id}/curso_materia/{curso_materia_id}", response_model=List[Participacion])
def read_participaciones_by_estudiante_and_curso_materia(
    estudiante_id: int,
    curso_materia_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    participaciones = db.query(Participaciones).filter(
        Participaciones.estudiante_id == estudiante_id,
        Participaciones.curso_materia_id == curso_materia_id
    ).all()

    return participaciones

@router.get(
    "/estudiante/{estudiante_id}/materia/{materia_id}/participaciones",
    response_model=List[ParticipacionConPeriodoResponse]
)
def read_participaciones_by_materia(
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

    participaciones = db.query(Participaciones).filter(
        Participaciones.estudiante_id == estudiante_id,
        Participaciones.curso_materia_id.in_(curso_materia_ids)
    ).options(
        joinedload(Participaciones.curso_materia)
        .joinedload(CursoMateria.curso_periodo)
        .joinedload(CursoPeriodo.periodo)
    ).all()

    resultado = []
    for p in participaciones:
        periodo = p.curso_materia.curso_periodo.periodo
        resultado.append({
            "id": p.id,
            "curso_materia_id": p.curso_materia_id,
            "estudiante_id": p.estudiante_id,
            "participacion_clase": p.participacion_clase,
            "fecha": p.fecha,
            "observacion": p.observacion,
            "periodo": {
                "bimestre": periodo.bimestre,
                "anio": periodo.anio,
                "descripcion": periodo.descripcion
            }
        })

    return resultado




@router.delete("/{participacion_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_participacion(participacion_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    db_participacion = db.query(Participaciones).filter(Participaciones.id == participacion_id).first()
    if db_participacion is None:
        raise HTTPException(status_code=404, detail="Participación no encontrada")
    
    db.delete(db_participacion)
    db.commit()
    return None
