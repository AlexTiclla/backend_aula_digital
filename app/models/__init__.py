# app/models/__init__.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import enum
from datetime import datetime

Base = declarative_base()

class RolUsuario(enum.Enum):
    ESTUDIANTE = "estudiante"
    PROFESOR = "profesor"
    ADMINISTRATIVO = "administrativo"

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    apellido = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    rol = Column(Enum(RolUsuario), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relación uno a uno con los perfiles específicos
    estudiante = relationship("Estudiante", back_populates="usuario", uselist=False)
    profesor = relationship("Profesor", back_populates="usuario", uselist=False)
    administrativo = relationship("Administrativo", back_populates="usuario", uselist=False)

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

class Profesor(Base):
    __tablename__ = "profesores"
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), unique=True, nullable=False)
    telefono = Column(String)
    carnet_identidad = Column(String, unique=True)
    especialidad = Column(String)
    nivel_academico = Column(String)
    
    # Relación con usuario
    usuario = relationship("Usuario", back_populates="profesor")

class Administrativo(Base):
    __tablename__ = "administrativos"
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), unique=True, nullable=False)
    
    # Relación con usuario
    usuario = relationship("Usuario", back_populates="administrativo")