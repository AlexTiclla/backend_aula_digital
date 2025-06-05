from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
# creo que es el schema ubicado en usr
from .users import EstudianteResponse
from .curso_materia import CursoMateriaResponse
from .nota import NotaResponse
from .asistencia import Asistencia
from .participacion import Participacion

class PrediccionRequest(BaseModel):
    estudiante_id: int
    # curso_materia_id: int

class PrediccionResponse(BaseModel):
    estudiante: EstudianteResponse
    # curso_materia: CursoMateriaResponse
    prediccion_nota: Optional[int] = None
    prediccion_asistencia: bool = False
    prediccion_participacion: bool = False
    confianza_nota: float = 0.0
    confianza_asistencia: float = 0.0
    confianza_participacion: float = 0.0
    ultimas_notas: List[NotaResponse] = []
    ultimas_asistencias: List[Asistencia] = []
    ultimas_participaciones: List[Participacion] = []

    class Config:
        from_attributes = True 