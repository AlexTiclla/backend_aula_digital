from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from .routers import auth, estudiantes, profesores, usuarios, tutores, curso,periodo,curso_periodo,materia,curso_materia, nota
from .config import settings



# Configuración de la documentación de Swagger UI
description = """
# API Aula Digital

API para la gestión de estudiantes, profesores y notas.
"""

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=description,
    version="1.0.0",
    openapi_url=f"/{settings.API_V1_STR.lstrip('/')}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configuración CORS para permitir solicitudes desde la aplicación móvil
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, limitar a los orígenes específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar Bearer Token en Swagger UI (sin username/password)
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=settings.PROJECT_NAME,
        version="1.0.0",
        description=description,
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"bearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Incluir los routers
app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(estudiantes.router)
app.include_router(profesores.router)
app.include_router(tutores.router)
app.include_router(curso.router)
app.include_router(periodo.router)
app.include_router(curso_periodo.router)
app.include_router(materia.router)
app.include_router(curso_materia.router)
app.include_router(nota.router)
