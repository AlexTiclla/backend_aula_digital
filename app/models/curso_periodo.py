from sqlalchemy import Column, Integer, ForeignKey, String, Boolean
from sqlalchemy.orm import relationship
from ..database import Base

class CursoPeriodo(Base):
    __tablename__ = "curso_periodo"

    id = Column(Integer, primary_key=True, index=True)
    curso_id = Column(Integer, ForeignKey("curso.id"))
    periodo_id = Column(Integer, ForeignKey("periodo.id"))
    aula = Column(String)
    turno = Column(String)
    capacidad_actual = Column(Integer)
    is_active = Column(Boolean, default=True)

    curso = relationship("Curso", back_populates="curso_periodos")
    periodo = relationship("Periodo", back_populates="curso_periodos")
    curso_materias = relationship("CursoMateria", back_populates="curso_periodo")
    
