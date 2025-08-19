from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from database import get_db
from models.usuario import Usuario
from routes.auth import get_current_user
import cloudinary
import cloudinary.uploader
import os
from typing import Optional

router = APIRouter()

# Configurar Cloudinary
cloudinary.config(
    cloud_name="dadw1qx7z",
    api_key="433556989533495",
    api_secret="LWRzwjfu9xlgGd41EQE2hdCY7sw"
)

@router.post("/profile-photo", summary="Subir foto de perfil")
async def upload_profile_photo(
    file: UploadFile = File(...),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Sube una foto de perfil para el usuario autenticado
    """
    try:
        # Validar tipo de archivo
        if not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo se permiten archivos de imagen"
            )
        
        # Validar tamaño (máximo 5MB)
        if file.size and file.size > 5 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El archivo es demasiado grande. Máximo 5MB"
            )
        
        # Leer el contenido del archivo
        file_content = await file.read()
        
        # Subir a Cloudinary
        upload_result = cloudinary.uploader.upload(
            file_content,
            folder="geoplanner/profile_photos",
            public_id=f"user_{current_user.id}",
            overwrite=True,
            resource_type="image"
        )
        
        # Obtener la URL de la imagen
        image_url = upload_result.get('secure_url')
        
        if not image_url:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al subir la imagen"
            )
        
        # Actualizar la URL en la base de datos
        current_user.foto_perfil_url = image_url
        db.commit()
        db.refresh(current_user)
        
        return {
            "mensaje": "Foto de perfil actualizada correctamente",
            "foto_perfil_url": image_url,
            "usuario": {
                "id": str(current_user.id),
                "nombre_usuario": current_user.nombre_usuario,
                "nombre": current_user.nombre,
                "apellido": current_user.apellido,
                "foto_perfil_url": current_user.foto_perfil_url
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al subir foto de perfil: {str(e)}"
        )

@router.delete("/profile-photo", summary="Eliminar foto de perfil")
async def delete_profile_photo(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Elimina la foto de perfil del usuario autenticado
    """
    try:
        if not current_user.foto_perfil_url:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No hay foto de perfil para eliminar"
            )
        
        # Eliminar de Cloudinary si es posible
        try:
            public_id = f"geoplanner/profile_photos/user_{current_user.id}"
            cloudinary.uploader.destroy(public_id)
        except Exception:
            # Si falla la eliminación en Cloudinary, continuar
            pass
        
        # Limpiar la URL en la base de datos
        current_user.foto_perfil_url = None
        db.commit()
        db.refresh(current_user)
        
        return {
            "mensaje": "Foto de perfil eliminada correctamente",
            "usuario": {
                "id": str(current_user.id),
                "nombre_usuario": current_user.nombre_usuario,
                "nombre": current_user.nombre,
                "apellido": current_user.apellido,
                "foto_perfil_url": current_user.foto_perfil_url
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar foto de perfil: {str(e)}"
        )
