from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class NotaBase(BaseModel):
    estudiante_id: int
    curso_materia_id: int
    valor: int
    descripcion: Optional[str] = None
    rendimiento: Optional[str] = None

class NotaCreate(NotaBase):
    pass

class NotaUpdate(BaseModel):
    valor: Optional[int] = None
    descripcion: Optional[str] = None
    rendimiento: Optional[str] = None
    fecha: Optional[datetime] = None

class NotaResponse(NotaBase):
    id: int
    fecha: datetime

    class Config:
        orm_mode = True
