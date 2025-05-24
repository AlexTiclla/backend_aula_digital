# app/routers/profesores.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Usuario, Profesor, RolUsuario
from ..schemas.users import ProfesorResponse, ProfesorCreate, ProfesorUpdate
from ..dependencies.auth import get_current_user, get_current_admin

router = APIRouter(prefix="/api/v1/profesores", tags=["profesores"])

@router.get("/", response_model=List[ProfesorResponse])
async def get_profesores(
    skip: int = 0, 
    limit: int = 100,
    current_user: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Obtener todos los profesores.
    Solo accesible para administradores.
    """
    profesores = db.query(Profesor).offset(skip).limit(limit).all()
    result = []
    for profesor in profesores:
        usuario = db.query(Usuario).filter(Usuario.id == profesor.usuario_id).first()
        if usuario:
            result.append({
                "id": profesor.id,
                "usuario_id": usuario.id,
                "nombre": usuario.nombre,
                "apellido": usuario.apellido,
                "email": usuario.email,
                "telefono": profesor.telefono,
                "carnet_identidad": profesor.carnet_identidad,
                "especialidad": profesor.especialidad,
                "nivel_academico": profesor.nivel_academico
            })
    return result

@router.get("/{usuario_id}", response_model=ProfesorResponse)
async def get_profesor(
    usuario_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener un profesor por ID de usuario.
    Un profesor puede ver su propio perfil, un administrador puede ver cualquier perfil.
    """
    # Verificar si el usuario actual es el mismo que se está solicitando o es un admin
    if current_user.id != usuario_id and current_user.rol != RolUsuario.ADMINISTRATIVO:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver este perfil"
        )
    
    # Verificar si el usuario existe
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con ID {usuario_id} no encontrado"
        )
    
    # Buscar el profesor
    profesor = db.query(Profesor).filter(Profesor.usuario_id == usuario_id).first()
    if not profesor:
        # Si el usuario existe pero no tiene perfil de profesor, crearlo automáticamente
        if usuario.rol == RolUsuario.PROFESOR:
            # Crear registro de profesor
            profesor = Profesor(
                usuario_id=usuario_id
            )
            db.add(profesor)
            db.commit()
            db.refresh(profesor)
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Perfil de profesor para usuario con ID {usuario_id} no encontrado. El usuario tiene rol: {usuario.rol.value}"
            )
    
    # Construir la respuesta combinando datos de ambas tablas
    return {
        "id": profesor.id,
        "usuario_id": usuario.id,
        "nombre": usuario.nombre,
        "apellido": usuario.apellido,
        "email": usuario.email,
        "telefono": profesor.telefono,
        "carnet_identidad": profesor.carnet_identidad,
        "especialidad": profesor.especialidad,
        "nivel_academico": profesor.nivel_academico
    }

@router.post("/", response_model=ProfesorResponse)
async def create_profesor(
    profesor_data: ProfesorCreate,
    current_user: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Crear un nuevo profesor.
    Solo accesible para administradores.
    """
    # Verificar si ya existe un profesor con ese usuario_id
    if db.query(Profesor).filter(Profesor.usuario_id == profesor_data.usuario_id).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un profesor con ese usuario_id"
        )
    
    # Verificar si existe el usuario
    usuario = db.query(Usuario).filter(Usuario.id == profesor_data.usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Crear el profesor
    profesor = Profesor(**profesor_data.dict())
    db.add(profesor)
    db.commit()
    db.refresh(profesor)
    
    # Construir la respuesta
    return {
        "id": profesor.id,
        "usuario_id": usuario.id,
        "nombre": usuario.nombre,
        "apellido": usuario.apellido,
        "email": usuario.email,
        "telefono": profesor.telefono,
        "carnet_identidad": profesor.carnet_identidad,
        "especialidad": profesor.especialidad,
        "nivel_academico": profesor.nivel_academico
    }

@router.put("/{profesor_id}", response_model=ProfesorResponse)
async def update_profesor(
    profesor_id: int,
    profesor_data: ProfesorUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualizar un profesor por ID.
    Un profesor puede actualizar su propio perfil, un administrador puede actualizar cualquier perfil.
    """
    # Buscar el profesor
    profesor = db.query(Profesor).filter(Profesor.id == profesor_id).first()
    if not profesor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profesor no encontrado"
        )
    
    # Verificar permiso
    if current_user.id != profesor.usuario_id and current_user.rol != RolUsuario.ADMINISTRATIVO:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para actualizar este perfil"
        )
    
    # Actualizar solo los campos proporcionados
    update_data = profesor_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(profesor, key, value)
    
    db.commit()
    db.refresh(profesor)
    
    # Obtener datos del usuario
    usuario = db.query(Usuario).filter(Usuario.id == profesor.usuario_id).first()
    
    # Construir la respuesta
    return {
        "id": profesor.id,
        "usuario_id": usuario.id,
        "nombre": usuario.nombre,
        "apellido": usuario.apellido,
        "email": usuario.email,
        "telefono": profesor.telefono,
        "carnet_identidad": profesor.carnet_identidad,
        "especialidad": profesor.especialidad,
        "nivel_academico": profesor.nivel_academico
    }

@router.delete("/{profesor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profesor(
    profesor_id: int,
    current_user: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Eliminar un profesor.
    Solo accesible para administradores.
    """
    profesor = db.query(Profesor).filter(Profesor.id == profesor_id).first()
    if not profesor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profesor no encontrado"
        )
    
    db.delete(profesor)
    db.commit()
    return None