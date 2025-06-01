from pydantic import BaseModel
from typing import Optional

class MateriaBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    area_conocimiento: str
    horas_semanales: int
    is_active: Optional[bool] = True

class MateriaCreate(MateriaBase):
    pass

class MateriaUpdate(BaseModel):
    nombre: Optional[str]
    descripcion: Optional[str]
    area_conocimiento: Optional[str]
    horas_semanales: Optional[int]
    is_active: Optional[bool]

class MateriaResponse(MateriaBase):
    id: int

    class Config:
        from_attributes = True
