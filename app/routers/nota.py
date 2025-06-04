from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from ..database import get_db
from ..models import CursoMateria, CursoPeriodo, Estudiante, Nota, Profesor
from ..schemas.nota import NotaConPeriodoResponse, NotaCreate, NotaDetalleResponse, NotaUpdate, NotaResponse, NotasConDetallesResponse
from ..dependencies.auth import get_current_admin, get_current_user

router = APIRouter(prefix="/api/v1/notas", tags=["notas"])

@router.post("/", response_model=NotaResponse)
async def crear_nota(nota: NotaCreate, db: Session = Depends(get_db), current_user=Depends(get_current_admin)):
    nuevo = Nota(**nota.dict())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.get("/", response_model=list[NotaResponse])
async def listar_notas(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(Nota).all()

@router.get("/estudiante/{estudiante_id}", response_model=list[NotaResponse])
async def listar_notas_por_estudiante(estudiante_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(Nota).filter(Nota.estudiante_id == estudiante_id).all()

@router.get("/curso_materia/{curso_materia_id}", response_model=list[NotaResponse])
async def listar_notas_por_curso_materia(curso_materia_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(Nota).filter(Nota.curso_materia_id == curso_materia_id).all()

@router.get(
    "/estudiante/{estudiante_id}/curso_materia/{curso_materia_id}/detalles",
    response_model=NotasConDetallesResponse
)
async def obtener_notas_con_detalles(
    estudiante_id: int,
    curso_materia_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Obtener estudiante con relación a usuario
    estudiante = db.query(Estudiante).options(
        joinedload(Estudiante.usuario)
    ).filter(Estudiante.id == estudiante_id).first()

    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")

    # Obtener curso_materia con todas las relaciones
    curso_materia = db.query(CursoMateria).options(
        joinedload(CursoMateria.materia),
        joinedload(CursoMateria.profesor).joinedload(CursoMateria.profesor.property.mapper.class_.usuario),
        joinedload(CursoMateria.curso_periodo).joinedload(CursoMateria.curso_periodo.property.mapper.class_.periodo)
    ).filter(CursoMateria.id == curso_materia_id).first()

    if not curso_materia:
        raise HTTPException(status_code=404, detail="Curso-Materia no encontrada")

    # Obtener todas las notas
    notas = db.query(Nota).filter(
        Nota.estudiante_id == estudiante_id,
        Nota.curso_materia_id == curso_materia_id
    ).all()

    # Construcción manual del esquema de respuesta
    return NotasConDetallesResponse(
        estudiante=estudiante,
        curso_materia=curso_materia,
        notas=[NotaDetalleResponse.from_orm(n) for n in notas]
    )
    
@router.get("/estudiante/{estudiante_id}/materia/{materia_id}/detalles", response_model=List[NotaConPeriodoResponse])
def listar_notas_por_materia_y_estudiante(
    estudiante_id: int,
    materia_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Buscar todas las curso_materia que tengan la materia solicitada
    curso_materias = (
        db.query(CursoMateria)
        .filter(CursoMateria.materia_id == materia_id)
        .options(
            joinedload(CursoMateria.curso_periodo).joinedload(CursoPeriodo.periodo),
            joinedload(CursoMateria.materia)
        )
        .all()
    )

    resultados = []

    for cm in curso_materias:
        notas = (
            db.query(Nota)
            .filter(
                Nota.estudiante_id == estudiante_id,
                Nota.curso_materia_id == cm.id
            )
            .all()
        )
        if notas:
            resultado = NotaConPeriodoResponse(
                periodo=cm.curso_periodo.periodo,
                curso_materia=cm,
                notas=notas
            )
            resultados.append(resultado)

    return resultados

@router.get("/{id}", response_model=NotaResponse)
async def obtener_nota(id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    obj = db.query(Nota).filter(Nota.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="No encontrado")
    return obj

@router.put("/{id}", response_model=NotaResponse)
async def actualizar_nota(id: int, data: NotaUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_admin)):
    obj = db.query(Nota).filter(Nota.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="No encontrado")
    for key, value in data.dict(exclude_unset=True).items():
        setattr(obj, key, value)
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/{id}")
async def eliminar_nota(id: int, db: Session = Depends(get_db), current_user=Depends(get_current_admin)):
    obj = db.query(Nota).filter(Nota.id == id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="No encontrado")
    db.delete(obj)
    db.commit()
    return {"message": "Eliminado"}
