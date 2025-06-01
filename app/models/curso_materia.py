from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from ..database import Base
from app.models.profesor import Profesor  # Importar la clase directamente
class CursoMateria(Base):
    __tablename__ = "curso_materia"

    id = Column(Integer, primary_key=True, index=True)
    materia_id = Column(Integer, ForeignKey("materia.id"), nullable=False)
    curso_periodo_id = Column(Integer, ForeignKey("curso_periodo.id"), nullable=False)
    profesor_id = Column(Integer, ForeignKey("profesores.id"), nullable=False)
    horario = Column(String, nullable=True)  # Puedes especificar formato (ej: "08:00-10:00")
    aula = Column(String, nullable=True)     # Aula donde se imparte la materia
    modalidad = Column(String, nullable=True)  # Presencial, virtual, híbrida, etc.
    
    # Relaciones con otras tablas
    curso_periodo = relationship("CursoPeriodo", back_populates="curso_materias")
    materia = relationship("Materia", back_populates="curso_materias")
    profesor = relationship(Profesor, back_populates="curso_materias")
