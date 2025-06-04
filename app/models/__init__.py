# app/models/__init__.py
from sqlalchemy import Column, Date, Integer, String, Boolean, DateTime, ForeignKey, Enum
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
    curso_materias = relationship("CursoMateria", back_populates="profesor")

class Administrativo(Base):
    __tablename__ = "administrativos"
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), unique=True, nullable=False)
    
    # Relación con usuario
    usuario = relationship("Usuario", back_populates="administrativo")

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

    

class Materia(Base):
    __tablename__ = "materia"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(String, nullable=True)
    area_conocimiento = Column(String, nullable=False)
    horas_semanales = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    curso_materias = relationship("CursoMateria", back_populates="materia")   

class Participaciones(Base):
    __tablename__ = "participaciones"
    id = Column(Integer, primary_key=True, index=True)
    estudiante_id = Column(Integer, ForeignKey("estudiantes.id"), nullable=False)
    curso_materia_id = Column(Integer, ForeignKey("curso_materia.id"), nullable=False)
    participacion_clase = Column(String, nullable=True)
    fecha = Column(DateTime, nullable=False, default=datetime.utcnow)
    observacion = Column(String, nullable=True)
    
    # Relaciones
    estudiante = relationship("Estudiante")
    curso_materia = relationship("CursoMateria")

class Asistencia(Base):
    __tablename__ = "asistencia"
    id = Column(Integer, primary_key=True, index=True)
    estudiante_id = Column(Integer, ForeignKey("estudiantes.id"), nullable=False)
    curso_materia_id = Column(Integer, ForeignKey("curso_materia.id"), nullable=False)
    valor = Column(Boolean, nullable=False)  # True para presente, False para ausente
    fecha = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relaciones
    estudiante = relationship("Estudiante")
    curso_materia = relationship("CursoMateria")

class Nota(Base):
    __tablename__ = "nota"
    id = Column(Integer, primary_key=True, index=True)
    estudiante_id = Column(Integer, ForeignKey("estudiantes.id"), nullable=False)
    curso_materia_id = Column(Integer, ForeignKey("curso_materia.id"), nullable=False)
    valor = Column(Integer, nullable=False)
    fecha = Column(DateTime, nullable=False, default=datetime.utcnow)
    descripcion = Column(String, nullable=True)
    rendimiento = Column(String, nullable=True)  # bajo, medio, alto
    
    # Relaciones
    estudiante = relationship("Estudiante")
    curso_materia = relationship("CursoMateria")