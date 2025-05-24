# app/schemas/users.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class EstudianteResponse(BaseModel):
    id: int
    usuario_id: int
    nombre: str
    apellido: str
    email: str
    direccion: Optional[str] = None
    fecha_nacimiento: Optional[datetime] = None

    class Config:
        from_attributes = True

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
    rol: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None