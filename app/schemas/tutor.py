from pydantic import BaseModel

class TutorResponse(BaseModel):
    id: int
    nombre: str
    apellido: str
    relacion_estudiante: str
    ocupacion: str
    lugar_trabajo: str
    correo: str
    telefono: str

    class Config:
        from_attributes = True
