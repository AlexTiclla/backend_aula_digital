from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from ..database import get_db
from ..models import Materia, CursoMateria, Estudiante, CursoPeriodo, Asistencia, Nota
from ..schemas.materia import MateriaCreate, MateriaUpdate, MateriaResponse
from ..dependencies.auth import get_current_admin, get_current_user

router = APIRouter(prefix="/api/v1/materias", tags=["materias"])

@router.post("/", response_model=MateriaResponse)
async def crear_materia(materia: MateriaCreate, db: Session = Depends(get_db), current_user=Depends(get_current_admin)):
    nuevo = Materia(**materia.dict())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.get("/", response_model=list[MateriaResponse])
async def listar_materias(db: Session = Depends(get_db)):
    return db.query(Materia).all()

@router.get("/estudiante/{estudiante_id}", response_model=List[dict])
async def obtener_materias_estudiante(
    estudiante_id: int, 
    db: Session = Depends(get_db), 
    current_user=Depends(get_current_user)
):
    """
    Obtener todas las materias en las que está inscrito un estudiante.
    """
    # Verificar si el estudiante existe
    estudiante = db.query(Estudiante).filter(Estudiante.id == estudiante_id).first()
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    
    # Obtener materias a través de asistencias y notas
    curso_materia_ids_from_asistencias = db.query(Asistencia.curso_materia_id)\
        .filter(Asistencia.estudiante_id == estudiante_id)\
        .distinct()\
        .all()
    
    curso_materia_ids_from_notas = db.query(Nota.curso_materia_id)\
        .filter(Nota.estudiante_id == estudiante_id)\
        .distinct()\
        .all()
    
    # Combinar IDs de curso_materia (eliminar duplicados)
    curso_materia_ids = set([cm_id[0] for cm_id in curso_materia_ids_from_asistencias] + 
                            [cm_id[0] for cm_id in curso_materia_ids_from_notas])
    
    # Si no hay materias asociadas al estudiante, devolver todas las materias disponibles
    if not curso_materia_ids:
        curso_materias = db.query(CursoMateria)\
            .join(Materia, CursoMateria.materia_id == Materia.id)\
            .options(
                joinedload(CursoMateria.materia),
                joinedload(CursoMateria.profesor).joinedload(CursoMateria.profesor.property.mapper.class_.usuario)
            )\
            .all()
    else:
        # Obtener curso_materias específicas del estudiante
        curso_materias = db.query(CursoMateria)\
            .join(Materia, CursoMateria.materia_id == Materia.id)\
            .filter(CursoMateria.id.in_(curso_materia_ids))\
            .options(
                joinedload(CursoMateria.materia),
                joinedload(CursoMateria.profesor).joinedload(CursoMateria.profesor.property.mapper.class_.usuario)
            )\
            .all()
    
    # Formatear la respuesta
    result = []
    for cm in curso_materias:
        profesor_nombre = f"{cm.profesor.usuario.nombre} {cm.profesor.usuario.apellido}" if cm.profesor and cm.profesor.usuario else "Sin profesor asignado"
        
        result.append({
            "id": cm.id,
            "nombre": cm.materia.nombre,
            "descripcion": cm.materia.descripcion,
            "areaConocimiento": cm.materia.area_conocimiento,
            "horasSemanales": cm.materia.horas_semanales,
            "profesorFullName": profesor_nombre,
            "horario": cm.horario or "No definido",
            "aula": cm.aula or "No definida",
            "modalidad": cm.modalidad or "Presencial"
        })
    
    return result

@router.get("/{id}", response_model=MateriaResponse)
async def obtener_materia(id: int, db: Session = Depends(get_db)):
    obj = db.query(Materia).filter(Materia.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="No encontrado")
    return obj

@router.put("/{id}", response_model=MateriaResponse)
async def actualizar_materia(id: int, data: MateriaUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_admin)):
    obj = db.query(Materia).filter(Materia.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="No encontrado")
    for key, value in data.dict(exclude_unset=True).items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/{id}")
async def eliminar_materia(id: int, db: Session = Depends(get_db), current_user=Depends(get_current_admin)):
    obj = db.query(Materia).filter(Materia.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="No encontrado")
    db.delete(obj)
    db.commit()
    return {"message": "Eliminado"}
