# app/schemas/auth.py
from pydantic import BaseModel, EmailStr, constr
from typing import Optional
from datetime import datetime
from enum import Enum

# app/schemas/auth.py
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: Optional[int] = None
    email: Optional[str] = None
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    rol: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    nombre: str
    apellido: str
    rol: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    nombre: str
    apellido: str
    rol: str
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True