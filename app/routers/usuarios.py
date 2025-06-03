# app/routers/usuarios.py
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Usuario, RolUsuario
from ..schemas.users import UsuarioCreate, UsuarioResponse, UsuarioUpdate
from ..dependencies.auth import get_current_user

router = APIRouter(prefix="/api/v1/usuarios", tags=["usuarios"])

@router.get("/", response_model=List[UsuarioResponse])
async def get_usuarios(
    skip: int = 0, 
    limit: int = 100,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener todos los usuarios.

    """
    usuarios = db.query(Usuario).offset(skip).limit(limit).all()
    return usuarios

@router.post("/", response_model=UsuarioResponse, status_code=201)
async def create_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    db_usuario = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    if db_usuario:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    nuevo_usuario = Usuario(
        nombre=usuario.nombre,
        apellido=usuario.apellido,
        email=usuario.email,
        password=usuario.password,  # O usa hash si corresponde
        rol=usuario.rol,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario

@router.get("/me", response_model=UsuarioResponse)
async def read_current_user(current_user: Usuario = Depends(get_current_user)):
    """
    Devuelve los datos del usuario autenticado.
    """
    return current_user

@router.get("/{usuario_id}", response_model=UsuarioResponse)
async def get_usuario(
    usuario_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener un usuario por ID.
    Un usuario puede ver su propio perfil.
    """
    # Verificar permiso
    if current_user.id != usuario_id and current_user.rol != RolUsuario.ADMINISTRATIVO:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver este perfil"
        )
    
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return usuario

@router.put("/{usuario_id}", response_model=UsuarioResponse)
async def update_usuario(
    usuario_id: int,
    usuario_data: UsuarioUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualizar un usuario.
    Un usuario puede actualizar su propio perfil.
    """
    # Verificar permiso
    if current_user.id != usuario_id and current_user.rol != RolUsuario.ADMINISTRATIVO:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para actualizar este perfil"
        )
    
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Actualizar solo los campos proporcionados
    update_data = usuario_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(usuario, key, value)
    
    db.commit()
    db.refresh(usuario)
    return usuario

@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_usuario(
    usuario_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Eliminar un usuario.

    """
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    db.delete(usuario)
    db.commit()
    return None 