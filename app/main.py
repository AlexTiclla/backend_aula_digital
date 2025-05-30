# app/main.py
from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, estudiantes, profesores, usuarios, tutores
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

# Configuración de seguridad para Swagger UI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

# Incluir los routers
app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(estudiantes.router)
app.include_router(profesores.router)
app.include_router(tutores.router)