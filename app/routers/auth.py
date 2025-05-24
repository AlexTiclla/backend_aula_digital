# app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Usuario, Tutor, Estudiante
from ..schemas.auth import LoginRequest, TokenResponse, UserCreate, UserResponse
from ..core.security import verify_password, create_access_token, get_password_hash
from fastapi.security import OAuth2PasswordRequestForm
from ..models import RolUsuario

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Verificar si el usuario ya existe
    if db.query(Usuario).filter(Usuario.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )
    
    # Crear nuevo usuario
    hashed_password = get_password_hash(user_data.password)
    db_user = Usuario(
        email=user_data.email,
        password=hashed_password,
        nombre=user_data.nombre,
        apellido=user_data.apellido,
        rol=user_data.rol,
        is_active=True
    )
    
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Si es un estudiante, crear también su registro en la tabla estudiantes
        if user_data.rol == RolUsuario.ESTUDIANTE:
            # Buscar un tutor por defecto o crear uno si no existe
            default_tutor = db.query(Tutor).first()
            if not default_tutor:
                default_tutor = Tutor(
                    nombre="Tutor",
                    apellido="Por Defecto",
                    relacion_estudiante="No especificado",
                    telefono="0000000000"
                )
                db.add(default_tutor)
                db.commit()
                db.refresh(default_tutor)
            
            # Verificar si ya existe un registro para este estudiante
            existing_estudiante = db.query(Estudiante).filter(Estudiante.usuario_id == db_user.id).first()
            if not existing_estudiante:
                # Crear registro de estudiante
                estudiante = Estudiante(
                    usuario_id=db_user.id,
                    tutor_id=default_tutor.id
                )
                db.add(estudiante)
                db.commit()
                db.refresh(estudiante)
        
        # Si es un profesor, crear también su registro en la tabla profesores
        elif user_data.rol == RolUsuario.PROFESOR:
            from ..models import Profesor
            # Verificar si ya existe un registro para este profesor
            existing_profesor = db.query(Profesor).filter(Profesor.usuario_id == db_user.id).first()
            if not existing_profesor:
                # Crear registro de profesor
                profesor = Profesor(
                    usuario_id=db_user.id
                )
                db.add(profesor)
                db.commit()
        
        return db_user
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear el usuario: {str(e)}"
        )

# Endpoint para la autenticación OAuth2 (Swagger UI)
@router.post("/token", response_model=TokenResponse)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(Usuario).filter(Usuario.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verificar si el usuario está activo
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )
    
    # Generar token
    token_data = {
        "sub": user.email,
        "user_id": user.id,
        "rol": user.rol.value
    }
    
    return {
        "access_token": create_access_token(token_data),
        "token_type": "bearer"
    }

# Endpoint para la API JSON (aplicación móvil)
@router.post("/login", response_model=TokenResponse)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )
    
    # Verificar si el usuario está activo
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )
    
    # Verificar y crear perfil si no existe
    if user.rol == RolUsuario.ESTUDIANTE:
        estudiante = db.query(Estudiante).filter(Estudiante.usuario_id == user.id).first()
        if not estudiante:
            # Buscar un tutor por defecto o crear uno si no existe
            default_tutor = db.query(Tutor).first()
            if not default_tutor:
                default_tutor = Tutor(
                    nombre="Tutor",
                    apellido="Por Defecto",
                    relacion_estudiante="No especificado",
                    telefono="0000000000"
                )
                db.add(default_tutor)
                db.commit()
                db.refresh(default_tutor)
            
            # Crear registro de estudiante
            estudiante = Estudiante(
                usuario_id=user.id,
                tutor_id=default_tutor.id
            )
            db.add(estudiante)
            db.commit()
    elif user.rol == RolUsuario.PROFESOR:
        from ..models import Profesor
        profesor = db.query(Profesor).filter(Profesor.usuario_id == user.id).first()
        if not profesor:
            # Crear registro de profesor
            profesor = Profesor(
                usuario_id=user.id
            )
            db.add(profesor)
            db.commit()
    
    # Generar token
    token_data = {
        "sub": user.email,
        "user_id": user.id,
        "rol": user.rol.value
    }
    
    return {
        "access_token": create_access_token(token_data),
        "token_type": "bearer",
        "user_id": user.id,
        "email": user.email,
        "nombre": user.nombre,
        "apellido": user.apellido,
        "rol": user.rol.value
    }