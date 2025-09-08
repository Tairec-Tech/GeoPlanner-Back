from pydantic import BaseModel, EmailStr

class UserRegister(BaseModel):
    nombre_usuario: str
    email: EmailStr
    password: str
    nombre: str
    apellido: str
    fecha_nacimiento: str  # formato: YYYY-MM-DD

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    nombre_usuario: str
    email: str
    nombre: str
    apellido: str

    class Config:
        from_attributes = True
