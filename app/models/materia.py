from sqlalchemy import Column, Integer, String, Boolean
from ..database import Base
from sqlalchemy.orm import relationship

class Materia(Base):
    __tablename__ = "materia"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(String, nullable=True)
    area_conocimiento = Column(String, nullable=False)
    horas_semanales = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)

    curso_materias = relationship("CursoMateria", back_populates="materia")
