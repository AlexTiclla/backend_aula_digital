from pydantic import BaseModel
from typing import Optional

class CursoBase(BaseModel):
    nombre: str
    sigla: str
    nivel: str
    capacidad_maxima: int
    descripcion: Optional[str] = None
    is_active: Optional[bool] = True

class CursoCreate(CursoBase):
    pass

class CursoUpdate(BaseModel):
    nombre: Optional[str]
    sigla: Optional[str]
    nivel: Optional[str]
    capacidad_maxima: Optional[int]
    descripcion: Optional[str]
    is_active: Optional[bool]

class CursoResponse(CursoBase):
    id: int

    class Config:
        from_attributes = True
