from datetime import datetime
import enum  # Para definir RolUsuario en otro archivo
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Date, Boolean, Enum as SqlEnum
from app.models import RolUsuario  # Asegúrate de que RolUsuario está bien definido
from ..database import Base
from sqlalchemy.orm import relationship
class Estudiante(Base):
    __tablename__ = "estudiantes"
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), unique=True, nullable=False)
    tutor_id = Column(Integer, ForeignKey('tutores.id'), nullable=False)  # Aquí está la clave foránea

    direccion = Column(String)
    fecha_nacimiento = Column(DateTime)
    
    # Relación
    usuario = relationship("Usuario", back_populates="estudiante")
    tutor = relationship("Tutor", back_populates="estudiantes")