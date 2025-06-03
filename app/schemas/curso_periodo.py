from pydantic import BaseModel
from typing import Optional

class CursoPeriodoBase(BaseModel):
    curso_id: int
    periodo_id: int
    aula: Optional[str] = None
    turno: Optional[str] = None
    capacidad_actual: Optional[int] = None
    is_active: Optional[bool] = True

class CursoPeriodoCreate(CursoPeriodoBase):
    pass

class CursoPeriodoUpdate(BaseModel):
    aula: Optional[str]
    turno: Optional[str]
    capacidad_actual: Optional[int]
    is_active: Optional[bool]

class CursoPeriodoResponse(BaseModel):
    id: int
    curso_id: int
    curso_nombre: Optional[str]  
    periodo_id: int
    periodo_nombre: Optional[str]  
    aula: str
    turno: str
    capacidad_actual: int
    is_active: bool

    class Config:
        from_attributes = True
