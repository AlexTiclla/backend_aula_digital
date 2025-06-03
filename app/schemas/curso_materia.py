from pydantic import BaseModel
from typing import Optional

class CursoMateriaBase(BaseModel):
    curso_periodo_id: int
    materia_id: int
    materiaNombre: Optional[str] = None
    profesor_id: int
    horario: Optional[str] = None
    aula: Optional[str] = None
    modalidad: Optional[str] = None

class CursoMateriaCreate(CursoMateriaBase):
    pass

class CursoMateriaUpdate(BaseModel):
    curso_periodo_id: Optional[int]
    materia_id: Optional[int]
    profesor_id: Optional[int]
    horario: Optional[str] = None
    aula: Optional[str] = None
    modalidad: Optional[str] = None

class CursoMateriaResponse(CursoMateriaBase):
    id: int

    class Config:
        from_attributes = True
