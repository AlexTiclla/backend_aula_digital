from pydantic import BaseModel, Field
from datetime import date
from typing import Optional

class PeriodoBase(BaseModel):
    bimestre: int = Field(..., ge=1, le=4)  # Limitar a 1-4
    anio: int
    fecha_inicio: date
    fecha_fin: date
    is_active: Optional[bool] = True
    descripcion: Optional[str] = None

class PeriodoCreate(PeriodoBase):
    pass

class PeriodoUpdate(BaseModel):
    bimestre: int = Field(..., ge=1, le=12)
    anio: Optional[int]
    fecha_inicio: Optional[date]
    fecha_fin: Optional[date]
    is_active: Optional[bool]
    descripcion: Optional[str]

class PeriodoResponse(PeriodoBase):
    id: int

    class Config:
        from_attributes = True
