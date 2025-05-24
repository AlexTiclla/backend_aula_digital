# app/routers/estudiantes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from ..database import get_db
from ..models import Usuario, Estudiante, Tutor, RolUsuario
from ..schemas.users import EstudianteResponse, EstudianteCreate, EstudianteUpdate
from ..dependencies.auth import get_current_user, get_current_admin

router = APIRouter(prefix="/api/v1/estudiantes", tags=["estudiantes"])

@router.get("/", response_model=List[EstudianteResponse])
async def get_estudiantes(
    skip: int = 0, 
    limit: int = 100,
    current_user: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Obtener todos los estudiantes.
    Solo accesible para administradores.
    """
    estudiantes = db.query(Estudiante).offset(skip).limit(limit).all()
    result = []
    for estudiante in estudiantes:
        usuario = db.query(Usuario).filter(Usuario.id == estudiante.usuario_id).first()
        if usuario:
            result.append({
                "id": estudiante.id,
                "usuario_id": usuario.id,
                "nombre": usuario.nombre,
                "apellido": usuario.apellido,
                "email": usuario.email,
                "direccion": estudiante.direccion,
                "fecha_nacimiento": estudiante.fecha_nacimiento
            })
    return result

@router.get("/{usuario_id}", response_model=EstudianteResponse)
async def get_estudiante(
    usuario_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener un estudiante por ID de usuario.
    Un estudiante puede ver su propio perfil, un administrador puede ver cualquier perfil.
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
    
    # Buscar el estudiante y unirlo con la tabla usuarios
    estudiante = db.query(Estudiante).filter(Estudiante.usuario_id == usuario_id).first()
    if not estudiante:
        # Si el usuario existe pero no tiene perfil de estudiante, crearlo automáticamente
        if usuario.rol == RolUsuario.ESTUDIANTE:
            # Buscar un tutor por defecto o crear uno si no existe
            default_tutor = db.query(Tutor).first()
            if not default_tutor:
                default_tutor = Tutor(
                    nombre="Tutor",
                    apellido="Por Defecto",
                    relacion_estudiante="No especificado",
                    telefono="0000000000"
                )
                db.add(default_tutor)
                db.commit()
                db.refresh(default_tutor)
            
            # Crear registro de estudiante
            estudiante = Estudiante(
                usuario_id=usuario_id,
                tutor_id=default_tutor.id
            )
            db.add(estudiante)
            db.commit()
            db.refresh(estudiante)
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Perfil de estudiante para usuario con ID {usuario_id} no encontrado. El usuario tiene rol: {usuario.rol.value}"
            )
    
    # Construir la respuesta combinando datos de ambas tablas
    return {
        "id": estudiante.id,
        "usuario_id": usuario.id,
        "nombre": usuario.nombre,
        "apellido": usuario.apellido,
        "email": usuario.email,
        "direccion": estudiante.direccion,
        "fecha_nacimiento": estudiante.fecha_nacimiento
    }

@router.post("/", response_model=EstudianteResponse)
async def create_estudiante(
    estudiante_data: EstudianteCreate,
    current_user: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Crear un nuevo estudiante.
    Solo accesible para administradores.
    """
    # Verificar si ya existe un estudiante con ese usuario_id
    if db.query(Estudiante).filter(Estudiante.usuario_id == estudiante_data.usuario_id).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un estudiante con ese usuario_id"
        )
    
    # Verificar si existe el usuario
    usuario = db.query(Usuario).filter(Usuario.id == estudiante_data.usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Verificar si existe el tutor
    tutor = db.query(Tutor).filter(Tutor.id == estudiante_data.tutor_id).first()
    if not tutor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tutor no encontrado"
        )
    
    # Crear el estudiante
    estudiante = Estudiante(**estudiante_data.dict())
    db.add(estudiante)
    db.commit()
    db.refresh(estudiante)
    
    # Construir la respuesta
    return {
        "id": estudiante.id,
        "usuario_id": usuario.id,
        "nombre": usuario.nombre,
        "apellido": usuario.apellido,
        "email": usuario.email,
        "direccion": estudiante.direccion,
        "fecha_nacimiento": estudiante.fecha_nacimiento
    }

@router.put("/{estudiante_id}", response_model=EstudianteResponse)
async def update_estudiante(
    estudiante_id: int,
    estudiante_data: EstudianteUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualizar un estudiante por ID.
    Un estudiante puede actualizar su propio perfil, un administrador puede actualizar cualquier perfil.
    """
    # Buscar el estudiante
    estudiante = db.query(Estudiante).filter(Estudiante.id == estudiante_id).first()
    if not estudiante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estudiante no encontrado"
        )
    
    # Verificar permiso
    if current_user.id != estudiante.usuario_id and current_user.rol != RolUsuario.ADMINISTRATIVO:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para actualizar este perfil"
        )
    
    # Si se proporciona tutor_id, verificar que existe
    if estudiante_data.tutor_id is not None:
        tutor = db.query(Tutor).filter(Tutor.id == estudiante_data.tutor_id).first()
        if not tutor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tutor no encontrado"
            )
    
    # Actualizar solo los campos proporcionados
    update_data = estudiante_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(estudiante, key, value)
    
    db.commit()
    db.refresh(estudiante)
    
    # Obtener datos del usuario
    usuario = db.query(Usuario).filter(Usuario.id == estudiante.usuario_id).first()
    
    # Construir la respuesta
    return {
        "id": estudiante.id,
        "usuario_id": usuario.id,
        "nombre": usuario.nombre,
        "apellido": usuario.apellido,
        "email": usuario.email,
        "direccion": estudiante.direccion,
        "fecha_nacimiento": estudiante.fecha_nacimiento
    }

@router.delete("/{estudiante_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_estudiante(
    estudiante_id: int,
    current_user: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Eliminar un estudiante.
    Solo accesible para administradores.
    """
    estudiante = db.query(Estudiante).filter(Estudiante.id == estudiante_id).first()
    if not estudiante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estudiante no encontrado"
        )
    
    db.delete(estudiante)
    db.commit()
    return None