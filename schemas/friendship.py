from pydantic import BaseModel

class FriendshipRequest(BaseModel):
    id_usuario2: str

class FriendshipResponse(BaseModel):
    id_usuario1: str
    id_usuario2: str
    estado: str
    id_usuario_accion: str
    fecha_creacion: str

    class Config:
        orm_mode = True
