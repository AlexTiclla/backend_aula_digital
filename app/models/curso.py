from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from ..database import Base

class Curso(Base):
    __tablename__ = "curso"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    sigla = Column(String, nullable=False)
    nivel = Column(String, nullable=False)
    capacidad_maxima = Column(Integer, nullable=False)
    descripcion = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)

    # Relación con curso_periodo
    curso_periodos = relationship("CursoPeriodo", back_populates="curso")
