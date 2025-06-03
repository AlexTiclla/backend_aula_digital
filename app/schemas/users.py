# app/schemas/users.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from app.models import RolUsuario
from app.routers.tutores import TutorResponse



class ProfesorResponse(BaseModel):
    id: int
    usuario_id: int
    nombre: str
    apellido: str
    email: str
    telefono: Optional[str] = None
    carnet_identidad: Optional[str] = None
    especialidad: Optional[str] = None
    nivel_academico: Optional[str] = None

    class Config:
        from_attributes = True
        
  

class EstudianteCreate(BaseModel):
    usuario_id: int
    tutor_id: int
    direccion: Optional[str] = None
    fecha_nacimiento: Optional[datetime] = None
    curso_periodo_id: int  # ID del curso_periodo al que pertenece el estudiante

class EstudianteUpdate(BaseModel):
    tutor_id: Optional[int] = None
    direccion: Optional[str] = None
    fecha_nacimiento: Optional[datetime] = None

class ProfesorCreate(BaseModel):
    usuario_id: int
    telefono: Optional[str] = None
    carnet_identidad: Optional[str] = None
    especialidad: Optional[str] = None
    nivel_academico: Optional[str] = None

class ProfesorUpdate(BaseModel):
    telefono: Optional[str] = None
    carnet_identidad: Optional[str] = None
    especialidad: Optional[str] = None
    nivel_academico: Optional[str] = None

class UsuarioResponse(BaseModel):
    id: int
    email: str
    nombre: str
    apellido: str
    rol: RolUsuario
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
   
   
class EstudianteResponse(BaseModel):
    id: int
    direccion: Optional[str]
    fecha_nacimiento: Optional[datetime]
    curso_periodo_id: Optional[int]
    curso_periodo_nombre: Optional[str]
    usuario: UsuarioResponse
    tutor: Optional[TutorResponse]

    class Config:
        from_attributes = True      
        
class EstudianteFlatResponse(BaseModel):
    id: int
    usuario_id: Optional[int]
    nombre: str
    apellido: str
    email: str
    direccion: str
    fecha_nacimiento: str
    tutor_id: Optional[int]
    tutor_nombre: Optional[str]
    rol: Optional[str]
    curso_periodo_id: Optional[int]
    curso_periodo_nombre: Optional[str]          

class ProfesorResponseWithUsuario(BaseModel):
    id: int
    usuario: UsuarioResponse  # Relación completa con el usuario
    telefono: Optional[str] = None
    carnet_identidad: Optional[str] = None
    especialidad: Optional[str] = None
    nivel_academico: Optional[str] = None

    class Config:
        from_attributes = True              

class UsuarioCreate(BaseModel):
    nombre: str
    apellido: str
    email: str
    password: str
    rol: RolUsuario  # Enum de roles: ESTUDIANTE, PROFESOR, ADMINISTRATIVO        

class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None