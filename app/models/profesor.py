from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from ..database import Base
from app.models.usuario import Usuario  # Importación directa

class Profesor(Base):
    __tablename__ = "profesores"
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), unique=True, nullable=False)
    telefono = Column(String)
    carnet_identidad = Column(String, unique=True)
    especialidad = Column(String)
    nivel_academico = Column(String)

    usuario = relationship(Usuario, back_populates="profesor")
    curso_materias = relationship("CursoMateria", back_populates="profesor")
