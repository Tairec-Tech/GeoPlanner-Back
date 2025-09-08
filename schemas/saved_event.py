from pydantic import BaseModel

class SaveEventRequest(BaseModel):
    id_publicacion: str

class SavedEventResponse(BaseModel):
    id_usuario: str
    id_publicacion: str
    fecha_guardado: str

    class Config:
        from_attributes = True
