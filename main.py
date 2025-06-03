from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, usuario, estudiante, profesor, administrativo, tutor, curso, periodo, materia, nota
from app.database import Base, engine

# Crear tablas en la base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API Aula Digital",
    description="API para la aplicación Aula Digital",
    version="1.0.0",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todos los orígenes
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos
    allow_headers=["*"],  # Permitir todos los headers
)

# Incluir routers
app.include_router(auth.router)
app.include_router(usuario.router)
app.include_router(estudiante.router)
app.include_router(profesor.router)
app.include_router(administrativo.router)
app.include_router(tutor.router)
app.include_router(curso.router)
app.include_router(periodo.router)
app.include_router(materia.router)
app.include_router(nota.router)

@app.get("/")
async def root():
    return {"message": "Bienvenido a la API de Aula Digital"} 