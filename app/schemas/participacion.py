from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ParticipacionBase(BaseModel):
    estudiante_id: int
    curso_materia_id: int
    participacion_clase: Optional[str] = None
    fecha: datetime = datetime.utcnow()
    observacion: Optional[str] = None

class ParticipacionCreate(ParticipacionBase):
    pass

class ParticipacionUpdate(BaseModel):
    participacion_clase: Optional[str] = None
    observacion: Optional[str] = None
    fecha: Optional[datetime] = None

class Participacion(ParticipacionBase):
    id: int
    
    class Config:
        orm_mode = True

class ParticipacionResponse(BaseModel):
    id: int
    curso_materia_id: int
    estudiante_id: int
    participacion_clase: Optional[str]
    fecha: datetime
    observacion: Optional[str]

    class Config:
        orm_mode = True
        
class PeriodoData(BaseModel):
    bimestre: int
    anio: int
    descripcion: Optional[str]

    class Config:
        orm_mode = True

class ParticipacionConPeriodoResponse(BaseModel):
    id: int
    curso_materia_id: int
    estudiante_id: int
    participacion_clase: Optional[str]
    fecha: datetime
    observacion: Optional[str]
    periodo: PeriodoData

    class Config:
        orm_mode = True        