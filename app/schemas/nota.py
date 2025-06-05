from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

from app.schemas.materia import MateriaResponse
from app.schemas.periodo import PeriodoResponse
from app.schemas.users import ProfesorResponseWithUsuario, UsuarioResponse

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
        from_attributes = True


class NotaDetalleResponse(BaseModel):
    id: int
    valor: int
    descripcion: Optional[str]
    rendimiento: Optional[str]
    fecha: datetime

    class Config:
        from_attributes = True
        
class EstudianteInfoNota(BaseModel):
    id: int
    direccion: Optional[str]
    fecha_nacimiento: Optional[datetime]
    usuario: UsuarioResponse

    class Config:
        from_attributes = True  


class CursoPeriodoInfoNota(BaseModel):
    id: int
    aula: Optional[str]
    turno: Optional[str]
    capacidad_actual: Optional[int]
    periodo: PeriodoResponse  # relación anidada

    class Config:
        from_attributes = True              
        
class CursoMateriaInfoNota(BaseModel):
    id: int
    horario: Optional[str]
    aula: Optional[str]
    modalidad: Optional[str]
    materia: MateriaResponse
    profesor: ProfesorResponseWithUsuario
    curso_periodo: CursoPeriodoInfoNota  # ← Nueva relación agregada

    class Config:
        from_attributes = True     
        
class NotasConDetallesResponse(BaseModel):
    estudiante: EstudianteInfoNota
    curso_materia: CursoMateriaInfoNota
    notas: List[NotaDetalleResponse]        
    
    class Config:
        from_attributes = True  
        
class CursoMateriaBasica(BaseModel):
    id: int
    horario: Optional[str]
    aula: Optional[str]
    modalidad: Optional[str]
    materia: MateriaResponse

    class Config:
        from_attributes = True
        
class NotaConPeriodoResponse(BaseModel):
    periodo: PeriodoResponse
    curso_materia: CursoMateriaBasica
    notas: List[NotaDetalleResponse]   

class PeriodoItem(BaseModel):
    id: int
    bimestre: int
    anio: int
    descripcion: Optional[str]
    fecha_inicio: datetime
    fecha_fin: datetime
        
class NotaItem(BaseModel):
    valor: int
    fecha: datetime
    descripcion: Optional[str]
    rendimiento: Optional[str]


class AsistenciaItem(BaseModel):
    valor: bool
    fecha: datetime


class ParticipacionItem(BaseModel):
    participacion_clase: Optional[str]
    observacion: Optional[str]
    fecha: datetime

class CursoMateriaPeriodoItem(BaseModel):
    curso_materia_id: int
    periodo: PeriodoItem

    nota: Optional[NotaItem]
    asistencia: Optional[AsistenciaItem]
    participacion: Optional[ParticipacionItem]
    
class DetalleMateriaEstudianteResponse(BaseModel):
    materia_id: int
    materia_nombre: str
    registros: List[CursoMateriaPeriodoItem]             
    
    
    