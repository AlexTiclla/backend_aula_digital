# app/routers/tutores.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Tutor, Usuario, RolUsuario
from pydantic import BaseModel
from ..dependencies.auth import get_current_user

# Schemas
class TutorBase(BaseModel):
    nombre: str
    apellido: str
    relacion_estudiante: str
    telefono: str
    ocupacion: str = None
    lugar_trabajo: str = None
    correo: str = None

class TutorCreate(TutorBase):
    pass

class TutorUpdate(BaseModel):
    nombre: str = None
    apellido: str = None
    relacion_estudiante: str = None
    telefono: str = None
    ocupacion: str = None
    lugar_trabajo: str = None
    correo: str = None

class TutorResponse(TutorBase):
    id: int

    class Config:
        from_attributes = True

router = APIRouter(prefix="/api/v1/tutores", tags=["tutores"])

@router.get("/", response_model=List[TutorResponse])
async def get_tutores(
    skip: int = 0, 
    limit: int = 100,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener todos los tutores.
    Accesible para todos los usuarios autenticados.
    """
    tutores = db.query(Tutor).offset(skip).limit(limit).all()
    return tutores

@router.get("/{tutor_id}", response_model=TutorResponse)
async def get_tutor(
    tutor_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener un tutor por ID.
    Accesible para todos los usuarios autenticados.
    """
    tutor = db.query(Tutor).filter(Tutor.id == tutor_id).first()
    if not tutor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tutor no encontrado"
        )
    
    return tutor

@router.post("/", response_model=TutorResponse)
async def create_tutor(
    tutor_data: TutorCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crear un nuevo tutor.
    Solo accesible para administradores.
    """
    # Verificar si ya existe un tutor con ese correo
    if tutor_data.correo and db.query(Tutor).filter(Tutor.correo == tutor_data.correo).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un tutor con ese correo"
        )
    
    # Crear el tutor
    tutor = Tutor(**tutor_data.dict())
    db.add(tutor)
    db.commit()
    db.refresh(tutor)
    
    return tutor

@router.put("/{tutor_id}", response_model=TutorResponse)
async def update_tutor(
    tutor_id: int,
    tutor_data: TutorUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualizar un tutor por ID.
    Solo accesible para administradores.
    """
    tutor = db.query(Tutor).filter(Tutor.id == tutor_id).first()
    if not tutor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tutor no encontrado"
        )
    
    # Verificar si ya existe otro tutor con ese correo
    if tutor_data.correo and tutor_data.correo != tutor.correo:
        existing_tutor = db.query(Tutor).filter(Tutor.correo == tutor_data.correo).first()
        if existing_tutor:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un tutor con ese correo"
            )
    
    # Actualizar solo los campos proporcionados
    update_data = tutor_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(tutor, key, value)
    
    db.commit()
    db.refresh(tutor)
    
    return tutor

@router.delete("/{tutor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tutor(
    tutor_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Eliminar un tutor.
    Solo accesible para administradores.
    """
    tutor = db.query(Tutor).filter(Tutor.id == tutor_id).first()
    if not tutor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tutor no encontrado"
        )
    
    # Verificar si hay estudiantes asociados
    if tutor.estudiantes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar un tutor con estudiantes asociados"
        )
    
    db.delete(tutor)
    db.commit()
    return None 