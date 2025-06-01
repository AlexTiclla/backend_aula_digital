from datetime import datetime
import enum  # Para definir RolUsuario en otro archivo
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Date, Boolean, Enum as SqlEnum
from app.models import RolUsuario  # Asegúrate de que RolUsuario está bien definido
from ..database import Base
from sqlalchemy.orm import relationship

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    apellido = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    rol = Column(SqlEnum(RolUsuario), nullable=False)  # Usar SqlEnum aquí
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    estudiante = relationship("Estudiante", back_populates="usuario", uselist=False)
    profesor = relationship("Profesor", back_populates="usuario", uselist=False)
    administrativo = relationship("Administrativo", back_populates="usuario", uselist=False)
