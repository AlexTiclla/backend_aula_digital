from datetime import datetime
from enum import Enum
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Date, Boolean

from app.models import RolUsuario
from ..database import Base
from sqlalchemy.orm import relationship

class Tutor(Base):
    __tablename__ = "tutores"
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    apellido = Column(String, nullable=False)
    relacion_estudiante = Column(String, nullable=False)  # padre, madre, tío, etc.
    ocupacion = Column(String)
    lugar_trabajo = Column(String)
    correo = Column(String, unique=True)
    telefono = Column(String, nullable=False)
    
    # Relación uno a muchos con estudiantes
    estudiantes = relationship("Estudiante", back_populates="tutor")