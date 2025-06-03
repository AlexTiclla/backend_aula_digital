# app/routers/estudiantes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from ..database import get_db
from ..models import CursoPeriodo, Usuario, Estudiante, Tutor, RolUsuario
from ..schemas.users import EstudianteFlatResponse, EstudianteResponse, EstudianteCreate, EstudianteUpdate
from ..dependencies.auth import get_current_user

router = APIRouter(prefix="/api/v1/estudiantes", tags=["estudiantes"])

@router.get("/", response_model=List[EstudianteFlatResponse])
async def get_estudiantes(
    skip: int = 0, 
    limit: int = 100,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener todos los estudiantes con datos adicionales.
    Solo accesible para administradores.
    """
    estudiantes = db.query(Estudiante).options(
        joinedload(Estudiante.usuario),
        joinedload(Estudiante.tutor)
    ).offset(skip).limit(limit).all()

    result = []
    for estudiante in estudiantes:
        usuario = estudiante.usuario
        tutor = estudiante.tutor
        result.append({
    "id": estudiante.id,
    "usuario_id": usuario.id if usuario else None,
    "nombre": usuario.nombre if usuario else "",
    "apellido": usuario.apellido if usuario else "",
    "email": usuario.email if usuario else "",
    "direccion": estudiante.direccion if estudiante.direccion else "",
    "fecha_nacimiento": estudiante.fecha_nacimiento.isoformat() if estudiante.fecha_nacimiento else "",
    "tutor_id": tutor.id if tutor else None,
    "tutor_nombre": f"{tutor.nombre} {tutor.apellido}" if tutor else None,
    "rol": usuario.rol.value if usuario else None,
    "curso_periodo_id": estudiante.curso_periodo.id if estudiante.curso_periodo else None,
    "curso_periodo_nombre": f"{estudiante.curso_periodo.curso.nombre} - {estudiante.curso_periodo.periodo.anio}" if estudiante.curso_periodo else None,
    })
    return result

@router.get("/{estudiante_id}", response_model=EstudianteResponse)
async def get_estudiante(
    estudiante_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener un estudiante por ID (tabla estudiantes), incluyendo datos del usuario.
    Solo accesible por administradores o el propio estudiante.
    """
    estudiante = db.query(Estudiante).options(
        joinedload(Estudiante.usuario),
        joinedload(Estudiante.tutor),
        joinedload(Estudiante.curso_periodo).joinedload(CursoPeriodo.curso),
        joinedload(Estudiante.curso_periodo).joinedload(CursoPeriodo.periodo)
    ).filter(Estudiante.id == estudiante_id).first()

    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")

    usuario = estudiante.usuario
    tutor = estudiante.tutor
    curso_periodo = estudiante.curso_periodo

    # Permitir acceso si el usuario es el mismo o si es administrador
    if current_user.id != estudiante.usuario_id and current_user.rol != RolUsuario.ADMINISTRATIVO:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver este perfil")

    return {
        "id": estudiante.id,
        "usuario_id": usuario.id,
        "nombre": usuario.nombre,
        "apellido": usuario.apellido,
        "email": usuario.email,
        "direccion": estudiante.direccion,
        "fecha_nacimiento": estudiante.fecha_nacimiento.isoformat() if estudiante.fecha_nacimiento else None,
        "tutor_id": tutor.id if tutor else None,
        "tutor_nombre": f"{tutor.nombre} {tutor.apellido}" if tutor else None,
        "rol": usuario.rol.value if usuario.rol else None,
        "curso_periodo_id": curso_periodo.id if curso_periodo else None,
        "curso_periodo_nombre": f"{curso_periodo.curso.nombre} - {curso_periodo.periodo.descripcion}" if curso_periodo else None
    }


@router.post("/", response_model=EstudianteResponse)
async def create_estudiante(
    estudiante_data: EstudianteCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Validaciones previas (existencia de usuario y tutor) ya las tienes...

    # Crear el estudiante
    estudiante = Estudiante(**estudiante_data.dict())
    db.add(estudiante)
    db.commit()
    db.refresh(estudiante)

    usuario = db.query(Usuario).filter(Usuario.id == estudiante.usuario_id).first()
    tutor = db.query(Tutor).filter(Tutor.id == estudiante.tutor_id).first()
    curso_periodo = db.query(CursoPeriodo).options(
        joinedload(CursoPeriodo.curso),
        joinedload(CursoPeriodo.periodo)
    ).filter(CursoPeriodo.id == estudiante.curso_periodo_id).first()

    return {
        "id": estudiante.id,
        "usuario_id": usuario.id,
        "nombre": usuario.nombre,
        "apellido": usuario.apellido,
        "email": usuario.email,
        "direccion": estudiante.direccion,
        "fecha_nacimiento": estudiante.fecha_nacimiento.isoformat() if estudiante.fecha_nacimiento else None,
        "tutor_id": tutor.id if tutor else None,
        "tutor_nombre": f"{tutor.nombre} {tutor.apellido}" if tutor else None,
        "rol": usuario.rol.value if usuario.rol else None,
        "curso_periodo_id": curso_periodo.id if curso_periodo else None,
        "curso_periodo_nombre": f"{curso_periodo.curso.nombre} - {curso_periodo.periodo.descripcion}" if curso_periodo else None
    }


@router.put("/{estudiante_id}", response_model=EstudianteResponse)
async def update_estudiante(
    estudiante_id: int,
    estudiante_data: EstudianteUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    estudiante = db.query(Estudiante).filter(Estudiante.id == estudiante_id).first()
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")

    # Permisos
    if current_user.id != estudiante.usuario_id and current_user.rol != RolUsuario.ADMINISTRATIVO:
        raise HTTPException(status_code=403, detail="No tienes permiso para actualizar este perfil")

    # Validar tutor
    if estudiante_data.tutor_id is not None:
        tutor = db.query(Tutor).filter(Tutor.id == estudiante_data.tutor_id).first()
        if not tutor:
            raise HTTPException(status_code=404, detail="Tutor no encontrado")

    # Actualizar campos
    update_data = estudiante_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(estudiante, key, value)

    db.commit()
    db.refresh(estudiante)

    # Cargar datos relacionados
    usuario = db.query(Usuario).filter(Usuario.id == estudiante.usuario_id).first()
    tutor = estudiante.tutor
    curso_periodo = estudiante.curso_periodo

    return {
        "id": estudiante.id,
        "usuario_id": usuario.id,
        "nombre": usuario.nombre,
        "apellido": usuario.apellido,
        "email": usuario.email,
        "direccion": estudiante.direccion,
        "fecha_nacimiento": estudiante.fecha_nacimiento.isoformat() if estudiante.fecha_nacimiento else None,
        "tutor_id": tutor.id if tutor else None,
        "tutor_nombre": f"{tutor.nombre} {tutor.apellido}" if tutor else None,
        "rol": usuario.rol.value if usuario.rol else None,
        "curso_periodo_id": curso_periodo.id if curso_periodo else None,
        "curso_periodo_nombre": f"{curso_periodo.curso.nombre} - {curso_periodo.periodo.descripcion}" if curso_periodo else None
    }

@router.delete("/{estudiante_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_estudiante(
    estudiante_id: int,
    current_user: Usuario = Depends(get_current_user),
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