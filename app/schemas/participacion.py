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
        from_attributes = True
