# app/seed_data.py
from sqlalchemy.orm import Session
from datetime import datetime, UTC  # Agregamos UTC para corregir el warning
from .models import Usuario, Estudiante, Profesor, Administrativo, RolUsuario, Tutor
from .database import SessionLocal
from passlib.context import CryptContext

# Configurar el contexto de hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def seed_data():
    db = SessionLocal()
    try:
        # Crear tutor
        tutor1 = Tutor(
            nombre="Ana",
            apellido="Martínez",
            relacion_estudiante="madre",
            ocupacion="Ingeniera",
            lugar_trabajo="Empresa ABC",
            correo="ana.martinez@ejemplo.com",
            telefono="76543210"
        )
        db.add(tutor1)
        db.flush()

        # Crear usuario estudiante
        estudiante1 = Usuario(
            nombre="Juan",
            apellido="Pérez",
            email="juan.perez@ejemplo.com",
            password=get_password_hash("password123"),
            rol=RolUsuario.ESTUDIANTE,  # Cambiado aquí
            created_at=datetime.now(UTC),  # Corregido el warning
            is_active=True
        )
        db.add(estudiante1)
        db.flush()
        
        # Crear segundo estudiante
        estudiante2 = Usuario(
            nombre="María",
            apellido="Pérez",
            email="maria.perez@ejemplo.com",
            password=get_password_hash("password123"),
            rol=RolUsuario.ESTUDIANTE,  # Cambiado aquí
            created_at=datetime.now(UTC),  # Corregido el warning
            is_active=True
        )
        db.add(estudiante2)
        db.flush()

        # Crear usuario profesor
        profesor1 = Usuario(
            nombre="María",
            apellido="González",
            email="maria.gonzalez@ejemplo.com",
            password=get_password_hash("password123"),
            rol=RolUsuario.PROFESOR,  # Cambiado aquí
            created_at=datetime.now(UTC),  # Corregido el warning
            is_active=True
        )
        db.add(profesor1)
        db.flush()

        # Crear usuario administrativo
        admin1 = Usuario(
            nombre="Carlos",
            apellido="Rodríguez",
            email="carlos.rodriguez@ejemplo.com",
            password=get_password_hash("password123"),
            rol=RolUsuario.ADMINISTRATIVO,  # Cambiado aquí
            created_at=datetime.now(UTC),  # Corregido el warning
            is_active=True
        )
        db.add(admin1)
        db.flush()

        # Crear perfiles
        perfil_estudiante1 = Estudiante(
            usuario_id=estudiante1.id,
            tutor_id=tutor1.id,
            direccion="Calle 123",
            fecha_nacimiento=datetime(2000, 1, 1)
        )
        db.add(perfil_estudiante1)

        perfil_estudiante2 = Estudiante(
            usuario_id=estudiante2.id,
            tutor_id=tutor1.id,
            direccion="Calle 123",
            fecha_nacimiento=datetime(2002, 3, 15)
        )
        db.add(perfil_estudiante2)

        perfil_profesor1 = Profesor(
            usuario_id=profesor1.id,
            telefono="123456789",
            carnet_identidad="1234567",
            especialidad="Matemáticas",
            nivel_academico="Maestría"
        )
        db.add(perfil_profesor1)

        perfil_admin1 = Administrativo(
            usuario_id=admin1.id
        )
        db.add(perfil_admin1)

        db.commit()
        print("Datos de prueba insertados correctamente")
        
    except Exception as e:
        print(f"Error al insertar datos: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()