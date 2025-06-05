from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AsistenciaBase(BaseModel):
    estudiante_id: int
    curso_materia_id: int
    valor: bool  # True para presente, False para ausente
    fecha: datetime = datetime.utcnow()

class AsistenciaCreate(AsistenciaBase):
    pass

class AsistenciaUpdate(BaseModel):
    valor: Optional[bool] = None
    fecha: Optional[datetime] = None
 

class PeriodoData(BaseModel):
    bimestre: int
    anio: int
    descripcion: Optional[str]

    class Config:
        orm_mode = True

class AsistenciaConPeriodoResponse(BaseModel):
    id: int
    estudiante_id: int
    curso_materia_id: int
    valor: bool
    fecha: datetime
    periodo: PeriodoData

    class Config:
        orm_mode = True    

class Asistencia(AsistenciaBase):
    id: int
    
    class Config:
        orm_mode = True
