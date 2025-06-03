# app/dependencies/auth.py
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from ..database import get_db
from ..models import Usuario, RolUsuario
from ..core.security import verify_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Usuario:
    payload = verify_token(token)
    user_email = payload.get("sub")
    
    if user_email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )
    
    user = db.query(Usuario).filter(Usuario.email == user_email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )
    
    return user

async def get_current_admin(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    """
    Verifica si el usuario es administrador.
    """
    if current_user.rol != RolUsuario.ADMINISTRATIVO:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador"
        )
    return current_user