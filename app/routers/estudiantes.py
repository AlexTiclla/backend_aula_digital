# app/routers/estudiantes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List

from app.schemas.nota import DetalleMateriaEstudianteResponse
from ..database import get_db
from ..models import Asistencia, CursoPeriodo, Nota, Participaciones, Pertenece, Usuario, Estudiante, Tutor, RolUsuario, CursoMateria, Materia, Profesor
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
        })
    return result


@router.get("/{estudiante_id}", response_model=EstudianteFlatResponse)
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
        joinedload(Estudiante.tutor)
    ).filter(Estudiante.id == estudiante_id).first()

    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")

    usuario = estudiante.usuario
    tutor = estudiante.tutor

    # Permitir acceso si el usuario es el mismo o si es administrativo
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
    }



@router.post("/", response_model=EstudianteResponse)
async def create_estudiante(
    estudiante_data: EstudianteCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crear un nuevo estudiante.
    Solo accesible para usuarios con permisos administrativos.
    """

    # Crear el estudiante (ya sin curso_periodo_id)
    estudiante_dict = estudiante_data.dict()
    estudiante_dict.pop("curso_periodo_id", None)  # eliminar si aún está en el esquema por error
    estudiante = Estudiante(**estudiante_dict)

    db.add(estudiante)
    db.commit()
    db.refresh(estudiante)

    usuario = db.query(Usuario).filter(Usuario.id == estudiante.usuario_id).first()
    tutor = db.query(Tutor).filter(Tutor.id == estudiante.tutor_id).first()

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
    }



@router.put("/{estudiante_id}", response_model=EstudianteFlatResponse)
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

    # Validar tutor si se está actualizando
    if estudiante_data.tutor_id is not None:
        tutor = db.query(Tutor).filter(Tutor.id == estudiante_data.tutor_id).first()
        if not tutor:
            raise HTTPException(status_code=404, detail="Tutor no encontrado")

    # Actualizar campos
    update_data = estudiante_data.dict(exclude_unset=True)
    update_data.pop("curso_periodo_id", None)  # eliminar si llega por error
    for key, value in update_data.items():
        setattr(estudiante, key, value)

    db.commit()
    db.refresh(estudiante)

    # Cargar datos relacionados
    usuario = db.query(Usuario).filter(Usuario.id == estudiante.usuario_id).first()
    tutor = estudiante.tutor

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

@router.get("/{estudiante_id}/materias/{materia_id}/detalle", response_model=DetalleMateriaEstudianteResponse)
async def obtener_detalle_materia_estudiante(
    estudiante_id: int,
    materia_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    estudiante = db.query(Estudiante).filter_by(id=estudiante_id).first()
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")

    if current_user.id != estudiante.usuario_id and current_user.rol != RolUsuario.ADMINISTRATIVO:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver esta información")

    # Obtener todas las asignaciones curso_materia para esta materia
    curso_materias = db.query(CursoMateria).filter_by(materia_id=materia_id).options(
        joinedload(CursoMateria.curso_periodo).joinedload(CursoPeriodo.periodo),
        joinedload(CursoMateria.materia)
    ).all()

    registros = []

    for cm in curso_materias:
        # Filtrar registros por estudiante y curso_materia específico
        nota = db.query(Nota).filter_by(estudiante_id=estudiante_id, curso_materia_id=cm.id).first()
        asistencia = db.query(Asistencia).filter_by(estudiante_id=estudiante_id, curso_materia_id=cm.id).first()
        participacion = db.query(Participaciones).filter_by(estudiante_id=estudiante_id, curso_materia_id=cm.id).first()

        # Si no hay ningún registro, lo ignoramos
        if not any([nota, asistencia, participacion]):
            continue

        periodo = cm.curso_periodo.periodo

        registros.append({
            "curso_materia_id": cm.id,
            "periodo": {
                "id": periodo.id,
                "bimestre": periodo.bimestre,
                "anio": periodo.anio,
                "descripcion": periodo.descripcion,
                "fecha_inicio": periodo.fecha_inicio,
                "fecha_fin": periodo.fecha_fin
            },
            "nota": {
                "valor": nota.valor,
                "fecha": nota.fecha,
                "descripcion": nota.descripcion,
                "rendimiento": nota.rendimiento
            } if nota else None,
            "asistencia": {
                "valor": asistencia.valor,
                "fecha": asistencia.fecha
            } if asistencia else None,
            "participacion": {
                "participacion_clase": participacion.participacion_clase,
                "observacion": participacion.observacion,
                "fecha": participacion.fecha
            } if participacion else None
        })

    if not registros:
        return DetalleMateriaEstudianteResponse(
            materia_id=materia_id,
            materia_nombre="",
            registros=[]
        )

    return DetalleMateriaEstudianteResponse(
        materia_id=materia_id,
        materia_nombre=curso_materias[0].materia.nombre,
        registros=registros
    )


@router.get("/{estudiante_id}/materias")
async def obtener_materias_estudiante(
    estudiante_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener todas las materias del curso actual de un estudiante.
    Un estudiante puede ver sus propias materias, un administrador puede ver las materias de cualquier estudiante.
    """
    # Buscar el estudiante
    estudiante = db.query(Estudiante).filter(Estudiante.id == estudiante_id).first()
    if not estudiante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estudiante no encontrado"
        )
    
    # Verificar permisos
    if current_user.id != estudiante.usuario_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver estas materias"
        )
    
    if not estudiante.curso_periodo_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El estudiante no tiene un curso asignado"
        )
    
    # Obtener todas las materias asociadas al curso_periodo del estudiante
    curso_materias = db.query(CursoMateria).filter(
        CursoMateria.curso_periodo_id == estudiante.curso_periodo_id
    ).options(
        joinedload(CursoMateria.materia),
        joinedload(CursoMateria.profesor).joinedload(Profesor.usuario)
    ).all()
    
    # Formatear los resultados
    materias = []
    for cm in curso_materias:
        materias.append({
            "id": cm.id,
            "materia": {
                "id": cm.materia.id,
                "nombre": cm.materia.nombre,
                "descripcion": cm.materia.descripcion,
                "area_conocimiento": cm.materia.area_conocimiento,
                "horas_semanales": cm.materia.horas_semanales
            },
            "profesor": {
                "id": cm.profesor.id,
                "nombre": cm.profesor.usuario.nombre,
                "apellido": cm.profesor.usuario.apellido,
                "especialidad": cm.profesor.especialidad
            },
            "horario": cm.horario,
            "aula": cm.aula,
            "modalidad": cm.modalidad
        })
    
    return materias


@router.get("/estudiantes/{estudiante_id}/materias2")
async def obtener_materias_sin_repetir(
    estudiante_id: int,
    db: Session = Depends(get_db)
):
    estudiante = db.query(Estudiante).filter_by(id=estudiante_id).first()
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")

    pertenece = db.query(Pertenece).filter_by(estudiante_id=estudiante_id).all()
    if not pertenece:
        return []

    curso_materia_ids = [p.curso_materia_id for p in pertenece]

    curso_materias = db.query(CursoMateria).filter(
        CursoMateria.id.in_(curso_materia_ids)
    ).options(
        joinedload(CursoMateria.materia),
        joinedload(CursoMateria.profesor).joinedload(Profesor.usuario)
    ).all()

    materias_vistas = set()
    resultado = []

    for cm in curso_materias:
        materia_id = cm.materia.id
        if materia_id in materias_vistas:
            continue  # saltar duplicados

        materias_vistas.add(materia_id)

        resultado.append({
            "id": cm.id,  # curso_materia_id de la primera inscripción encontrada
            "materia": {
                "id": cm.materia.id,
                "nombre": cm.materia.nombre,
                "descripcion": cm.materia.descripcion,
                "area_conocimiento": cm.materia.area_conocimiento,
                "horas_semanales": cm.materia.horas_semanales
            },
            "profesor": {
                "id": cm.profesor.id,
                "nombre": cm.profesor.usuario.nombre,
                "apellido": cm.profesor.usuario.apellido,
                "especialidad": cm.profesor.especialidad
            },
            "horario": cm.horario,
            "aula": cm.aula,
            "modalidad": cm.modalidad
        })

    return resultado

