# services/curso_service.py
from sqlalchemy.orm import Session
from models import CursoMateria

def obtener_estudiantes_por_curso_materia(db: Session):
    cursos = db.query(CursoMateria).all()
    resultado = []

    for curso in cursos:
        cantidad = len(curso.estudiantes)  # Asumiendo relación: CursoMateria.estudiantes
        resultado.append({
            "curso_materia_id": curso.id,
            "nombre": curso.nombre if hasattr(curso, "nombre") else f"CursoMateria {curso.id}",
            "cantidad_estudiantes": cantidad
        })

    return resultado
