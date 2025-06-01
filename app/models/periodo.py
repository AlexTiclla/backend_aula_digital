from sqlalchemy import Column, Integer, String, Date, Boolean
from ..database import Base
from sqlalchemy.orm import relationship

class Periodo(Base):
    __tablename__ = "periodo"

    id = Column(Integer, primary_key=True, index=True)
    bimestre = Column(Integer, nullable=False)  # Bimestre (1, 2, 3...)
    anio = Column(Integer, nullable=False)      # Año del periodo
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True)
    descripcion = Column(String, nullable=True)

    curso_periodos = relationship("CursoPeriodo", back_populates="periodo")
