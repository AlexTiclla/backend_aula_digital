# app/routers/profesores.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session,joinedload
from typing import List

from ..database import get_db
from ..models import Usuario, Profesor, RolUsuario, Estudiante, CursoMateria, Asistencia, Nota, Participaciones
from ..schemas.users import ProfesorResponse, ProfesorCreate, ProfesorResponseWithUsuario, ProfesorUpdate
from ..dependencies.auth import get_current_user

router = APIRouter(prefix="/api/v1/profesores", tags=["profesores"])

@router.get("/", response_model=List[ProfesorResponseWithUsuario])
async def get_profesores(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Validar permisos si es necesario
    # if current_user.rol != RolUsuario.ADMINISTRATIVO:
    #     raise HTTPException(status_code=403, detail="No tienes permiso para ver profesores")

    profesores = db.query(Profesor).options(joinedload(Profesor.usuario)).offset(skip).limit(limit).all()
    return profesores

@router.get("/{profesor_id}", response_model=ProfesorResponse)
async def get_profesor(
    profesor_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener un profesor por ID del profesor.
    Un profesor puede ver su propio perfil, un administrador puede ver cualquier perfil.
    """
    # Buscar el profesor por ID
    profesor = db.query(Profesor).options(joinedload(Profesor.usuario)).filter(Profesor.id == profesor_id).first()
    if not profesor:
        raise HTTPException(status_code=404, detail=f"Profesor con ID {profesor_id} no encontrado")

    # Verificar permisos: permitir al propio usuario o administrador
    if current_user.id != profesor.usuario_id and current_user.rol != RolUsuario.ADMINISTRATIVO:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver este perfil")

    usuario = profesor.usuario
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario asociado al profesor no encontrado")

    # Construir la respuesta combinada
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
@router.post("/", response_model=ProfesorResponseWithUsuario)
async def create_profesor(
    profesor_data: ProfesorCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Validar permisos (opcional)
    if current_user.rol != RolUsuario.ADMINISTRATIVO:
        raise HTTPException(status_code=403, detail="No tienes permiso para crear profesores")

    # Verificar duplicado
    if db.query(Profesor).filter(Profesor.usuario_id == profesor_data.usuario_id).first():
        raise HTTPException(status_code=400, detail="Ya existe un profesor con ese usuario_id")

    # Verificar existencia del usuario
    usuario = db.query(Usuario).filter(Usuario.id == profesor_data.usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Crear el profesor
    profesor = Profesor(**profesor_data.dict())
    db.add(profesor)
    db.commit()
    db.refresh(profesor)

    # Cargar relación con usuario
    profesor = db.query(Profesor).options(joinedload(Profesor.usuario)).filter(Profesor.id == profesor.id).first()

    return profesor
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
    current_user: Usuario = Depends(get_current_user),
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

@router.get("/estudiante/{estudiante_id}", response_model=List[ProfesorResponse])
async def get_profesores_by_estudiante(
    estudiante_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener todos los profesores que imparten materias a un estudiante específico.
    Se obtienen a través de las relaciones en asistencias, notas y participaciones.
    """
    # Verificar que el estudiante existe
    estudiante = db.query(Estudiante).filter(Estudiante.id == estudiante_id).first()
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    
    # Obtener curso_materia_ids desde asistencias
    curso_materia_ids_from_asistencias = db.query(Asistencia.curso_materia_id)\
        .filter(Asistencia.estudiante_id == estudiante_id)\
        .distinct()\
        .all()
    
    # Obtener curso_materia_ids desde notas
    curso_materia_ids_from_notas = db.query(Nota.curso_materia_id)\
        .filter(Nota.estudiante_id == estudiante_id)\
        .distinct()\
        .all()
    
    # Obtener curso_materia_ids desde participaciones
    curso_materia_ids_from_participaciones = db.query(Participaciones.curso_materia_id)\
        .filter(Participaciones.estudiante_id == estudiante_id)\
        .distinct()\
        .all()
    
    # Combinar todos los IDs de curso_materia (eliminar duplicados)
    curso_materia_ids = set([cm_id[0] for cm_id in curso_materia_ids_from_asistencias] + 
                           [cm_id[0] for cm_id in curso_materia_ids_from_notas] +
                           [cm_id[0] for cm_id in curso_materia_ids_from_participaciones])
    
    if not curso_materia_ids:
        return []
    
    # Obtener profesores_ids desde curso_materias
    profesor_ids = db.query(CursoMateria.profesor_id)\
        .filter(CursoMateria.id.in_(curso_materia_ids))\
        .distinct()\
        .all()
    
    profesor_ids_list = [p_id[0] for p_id in profesor_ids]
    
    # Obtener información de profesores
    profesores = db.query(Profesor)\
        .options(joinedload(Profesor.usuario))\
        .filter(Profesor.id.in_(profesor_ids_list))\
        .all()
    
    result = []
    for profesor in profesores:
        usuario = profesor.usuario
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