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
 

class CursoMateriaEstudiantesResumen(BaseModel):
    curso_materia_id: int
    nombre_materia: str
    cantidad_estudiantes: int       
    
    class Config:
        from_attributes = True
  

class CursoMateriaPorPeriodoResponse(BaseModel):
    id: int
    nombre_materia: str
    curso_periodo_id: int

    class Config:
        orm_mode = True