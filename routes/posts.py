from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.publicacion import Publicacion
from models.usuario import Usuario
from models.like import Like
from models.amistad import Amistad
from routes.auth import get_current_user
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
import uuid
from datetime import datetime

router = APIRouter()

# Esquemas para publicaciones
class PostCreate(BaseModel):
    texto: str
    tipo: str  # 'Deporte', 'Social', 'Estudio', 'Cultural', 'Otro'
    fecha_evento: datetime
    privacidad: str = "publica"  # 'publica', 'amigos', 'privada'
    media_url: Optional[str] = None
    terminos_adicionales: Optional[str] = None
    rutas: Optional[List[dict]] = None

class PostResponse(BaseModel):
    id: str
    id_autor: str
    nombre_autor: str
    username_autor: str
    foto_autor: Optional[str] = None
    texto: str
    tipo: str
    fecha_evento: datetime
    privacidad: str
    media_url: Optional[str]
    terminos_adicionales: Optional[str]
    estado: str
    fecha_creacion: datetime
    likes: int = 0
    likers: List[str] = []
    rutas: Optional[List[dict]] = []
    
    class Config:
        from_attributes = True
        json_encoders = {
            UUID: lambda v: str(v)
        }

def get_blocked_users(user_id: str, db: Session) -> List[str]:
    """
    Obtiene la lista de usuarios bloqueados por el usuario actual
    """
    # Buscar relaciones donde el usuario actual bloqueó a otros
    blocked_relations = db.query(Amistad).filter(
        ((Amistad.id_usuario1 == user_id) | (Amistad.id_usuario2 == user_id)),
        Amistad.estado == "bloqueada",
        Amistad.id_usuario_accion == user_id  # El usuario actual es quien bloqueó
    ).all()
    
    blocked_users = []
    for relation in blocked_relations:
        if str(relation.id_usuario1) == user_id:
            blocked_users.append(str(relation.id_usuario2))
        else:
            blocked_users.append(str(relation.id_usuario1))
    
    return blocked_users

def get_users_who_blocked_me(user_id: str, db: Session) -> List[str]:
    """
    Obtiene la lista de usuarios que bloquearon al usuario actual
    """
    # Buscar relaciones donde otros bloquearon al usuario actual
    blocked_by_relations = db.query(Amistad).filter(
        ((Amistad.id_usuario1 == user_id) | (Amistad.id_usuario2 == user_id)),
        Amistad.estado == "bloqueada",
        Amistad.id_usuario_accion != user_id  # El usuario actual NO es quien bloqueó
    ).all()
    
    users_who_blocked = []
    for relation in blocked_by_relations:
        if str(relation.id_usuario1) == user_id:
            users_who_blocked.append(str(relation.id_usuario2))
        else:
            users_who_blocked.append(str(relation.id_usuario1))
    
    return users_who_blocked

@router.get("/", response_model=List[PostResponse], summary="Obtener publicaciones del usuario autenticado")
def get_posts(
    skip: int = 0, 
    limit: int = 100, 
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene las publicaciones del usuario autenticado y sus amigos, excluyendo usuarios bloqueados
    """
    try:
        # Obtener usuarios bloqueados y usuarios que me bloquearon
        blocked_users = get_blocked_users(str(current_user.id), db)
        users_who_blocked_me = get_users_who_blocked_me(str(current_user.id), db)
        
        # Combinar ambas listas para excluir completamente
        users_to_exclude = list(set(blocked_users + users_who_blocked_me))
        
        # Obtener publicaciones según las reglas de privacidad
        # 1. Públicas: todos pueden ver
        # 2. Privadas: solo el autor puede ver
        # 3. Amigos: solo amigos pueden ver
        # 4. Siempre incluir las publicaciones del usuario actual
        
        # Obtener amigos del usuario actual
        from models.amistad import Amistad
        friends_query = db.query(Amistad).filter(
            ((Amistad.id_usuario1 == str(current_user.id)) | (Amistad.id_usuario2 == str(current_user.id))) &
            (Amistad.estado == "aceptada")
        )
        friends = friends_query.all()
        
        # Crear lista de IDs de amigos
        friend_ids = []
        for friendship in friends:
            if str(friendship.id_usuario1) == str(current_user.id):
                friend_ids.append(str(friendship.id_usuario2))
            else:
                friend_ids.append(str(friendship.id_usuario1))
        
        # Construir la consulta con las reglas de privacidad
        posts_query = db.query(Publicacion).join(Usuario, Publicacion.id_autor == Usuario.id).filter(
            # Públicas: todos pueden ver
            (Publicacion.privacidad == "publica") |
            # Privadas: solo el autor puede ver
            ((Publicacion.privacidad == "privada") & (Publicacion.id_autor == str(current_user.id))) |
            # Amigos: solo amigos pueden ver
            ((Publicacion.privacidad == "amigos") & (Publicacion.id_autor.in_(friend_ids))) |
            # Siempre incluir las publicaciones del usuario actual
            (Publicacion.id_autor == str(current_user.id))
        )
        
        # Excluir publicaciones de usuarios bloqueados
        if users_to_exclude:
            posts_query = posts_query.filter(~Publicacion.id_autor.in_(users_to_exclude))
        
        posts = posts_query.offset(skip).limit(limit).all()
        
        # Convertir UUIDs a strings para cada post y agregar información de likes
        converted_posts = []
        for post in posts:
            # Obtener información de likes
            likes = db.query(Like).filter(Like.id_publicacion == str(post.id)).all()
            likers = [str(like.id_usuario) for like in likes]
            
            # Obtener rutas de la publicación
            rutas = []
            if hasattr(post, 'rutas') and post.rutas:
                for ruta in post.rutas:
                    rutas.append({
                        "latitud": ruta.latitud,
                        "longitud": ruta.longitud,
                        "etiqueta": ruta.etiqueta,
                        "orden": ruta.orden
                    })
            
            converted_posts.append({
                "id": str(post.id),
                "id_autor": str(post.id_autor),
                "nombre_autor": f"{post.autor.nombre} {post.autor.apellido}".strip(),
                "username_autor": post.autor.nombre_usuario,
                "foto_autor": post.autor.foto_perfil_url,
                "texto": post.texto,
                "tipo": post.tipo,
                "fecha_evento": post.fecha_evento,
                "privacidad": post.privacidad,
                "media_url": post.media_url,
                "terminos_adicionales": post.terminos_adicionales,
                "estado": post.estado,
                "fecha_creacion": post.fecha_creacion,
                "likes": len(likes),
                "likers": likers,
                "rutas": rutas
            })
        
        return converted_posts
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener publicaciones: {str(e)}"
        )

@router.get("/{post_id}", response_model=PostResponse, summary="Obtener publicación por ID")
def get_post(
    post_id: str, 
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene una publicación específica por su ID, respetando las reglas de privacidad
    """
    try:
        # Validar que el ID sea un UUID válido
        uuid.UUID(post_id)
        
        post = db.query(Publicacion).join(Usuario, Publicacion.id_autor == Usuario.id).filter(Publicacion.id == post_id).first()
        if post is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Publicación no encontrada"
            )
        
        # Verificar permisos de acceso según la privacidad
        can_access = False
        
        # El autor siempre puede ver sus publicaciones
        if str(post.id_autor) == str(current_user.id):
            can_access = True
        # Públicas: todos pueden ver
        elif post.privacidad == "publica":
            can_access = True
        # Privadas: solo el autor puede ver
        elif post.privacidad == "privada":
            can_access = str(post.id_autor) == str(current_user.id)
        # Amigos: solo amigos pueden ver
        elif post.privacidad == "amigos":
            from models.amistad import Amistad
            friendship = db.query(Amistad).filter(
                ((Amistad.id_usuario1 == str(current_user.id)) & (Amistad.id_usuario2 == str(post.id_autor))) |
                ((Amistad.id_usuario1 == str(post.id_autor)) & (Amistad.id_usuario2 == str(current_user.id))),
                Amistad.estado == "aceptada"
            ).first()
            can_access = friendship is not None
        
        if not can_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para ver esta publicación"
            )
        
        # Obtener información de likes
        likes = db.query(Like).filter(Like.id_publicacion == post_id).all()
        likers = [str(like.id_usuario) for like in likes]
        
        # Obtener rutas de la publicación
        rutas = []
        if hasattr(post, 'rutas') and post.rutas:
            for ruta in post.rutas:
                rutas.append({
                    "latitud": ruta.latitud,
                    "longitud": ruta.longitud,
                    "etiqueta": ruta.etiqueta,
                    "orden": ruta.orden
                })
        
        # Convertir UUIDs a strings
        return {
            "id": str(post.id),
            "id_autor": str(post.id_autor),
            "nombre_autor": f"{post.autor.nombre} {post.autor.apellido}".strip(),
            "username_autor": post.autor.nombre_usuario,
            "foto_autor": post.autor.foto_perfil_url,
            "texto": post.texto,
            "tipo": post.tipo,
            "fecha_evento": post.fecha_evento,
            "privacidad": post.privacidad,
            "media_url": post.media_url,
            "terminos_adicionales": post.terminos_adicionales,
            "estado": post.estado,
            "fecha_creacion": post.fecha_creacion,
            "likes": len(likes),
            "likers": likers,
            "rutas": rutas
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de publicación inválido"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener publicación: {str(e)}"
        )

@router.post("/", response_model=PostResponse, summary="Crear nueva publicación")
def create_post(
    post_data: PostCreate, 
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crea una nueva publicación para el usuario autenticado
    """
    try:
        # Crear nueva publicación
        new_post = Publicacion(
            id_autor=str(current_user.id),
            texto=post_data.texto,
            tipo=post_data.tipo,
            fecha_evento=post_data.fecha_evento,
            privacidad=post_data.privacidad,
            media_url=post_data.media_url,
            terminos_adicionales=post_data.terminos_adicionales
        )
        
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        
        # Crear rutas si se proporcionan
        if post_data.rutas:
            from models.ruta import Ruta
            for i, ruta_data in enumerate(post_data.rutas):
                ruta = Ruta(
                    id_publicacion=new_post.id,
                    latitud=ruta_data.get("latitud", 0),
                    longitud=ruta_data.get("longitud", 0),
                    etiqueta=ruta_data.get("etiqueta", f"Punto {i+1}"),
                    orden=ruta_data.get("orden", i)
                )
                db.add(ruta)
            
            db.commit()
        
        # Obtener información del autor
        autor = db.query(Usuario).filter(Usuario.id == current_user.id).first()
        
        # Convertir UUIDs a strings para la respuesta
        return {
            "id": str(new_post.id),
            "id_autor": str(new_post.id_autor),
            "nombre_autor": f"{autor.nombre} {autor.apellido}".strip(),
            "username_autor": autor.nombre_usuario,
            "foto_autor": autor.foto_perfil_url,
            "texto": new_post.texto,
            "tipo": new_post.tipo,
            "fecha_evento": new_post.fecha_evento,
            "privacidad": new_post.privacidad,
            "media_url": new_post.media_url,
            "terminos_adicionales": new_post.terminos_adicionales,
            "estado": new_post.estado,
            "fecha_creacion": new_post.fecha_creacion,
            "likes": 0,
            "likers": [],
            "rutas": []
        }
        
    except HTTPException:
        raise
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de autor inválido"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear publicación: {str(e)}"
        )

@router.get("/user/{user_id}", response_model=List[PostResponse], summary="Obtener publicaciones de un usuario")
def get_user_posts(user_id: str, db: Session = Depends(get_db)):
    """
    Obtiene todas las publicaciones de un usuario específico
    """
    try:
        # Validar que el ID sea un UUID válido
        uuid.UUID(user_id)
        
        posts = db.query(Publicacion).join(Usuario, Publicacion.id_autor == Usuario.id).filter(Publicacion.id_autor == user_id).all()
        
        # Convertir UUIDs a strings para cada post
        converted_posts = []
        for post in posts:
            # Obtener información de likes
            likes = db.query(Like).filter(Like.id_publicacion == str(post.id)).all()
            likers = [str(like.id_usuario) for like in likes]
            
            # Obtener rutas de la publicación
            rutas = []
            if hasattr(post, 'rutas') and post.rutas:
                for ruta in post.rutas:
                    rutas.append({
                        "latitud": ruta.latitud,
                        "longitud": ruta.longitud,
                        "etiqueta": ruta.etiqueta,
                        "orden": ruta.orden
                    })
            
            converted_posts.append({
                "id": str(post.id),
                "id_autor": str(post.id_autor),
                "nombre_autor": f"{post.autor.nombre} {post.autor.apellido}".strip(),
                "username_autor": post.autor.nombre_usuario,
                "foto_autor": post.autor.foto_perfil_url,
                "texto": post.texto,
                "tipo": post.tipo,
                "fecha_evento": post.fecha_evento,
                "privacidad": post.privacidad,
                "media_url": post.media_url,
                "terminos_adicionales": post.terminos_adicionales,
                "estado": post.estado,
                "fecha_creacion": post.fecha_creacion,
                "likes": len(likes),
                "likers": likers,
                "rutas": rutas
            })
        
        return converted_posts
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de usuario inválido"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener publicaciones del usuario: {str(e)}"
        )

@router.post("/{post_id}/inscribirse", summary="Inscribirse en un evento")
def inscribirse_evento(
    post_id: str,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Inscribe al usuario actual en un evento específico
    """
    try:
        # Validar que el post_id sea un UUID válido
        uuid.UUID(post_id)
        
        # Verificar que la publicación existe
        publicacion = db.query(Publicacion).filter(Publicacion.id == post_id).first()
        if not publicacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Publicación no encontrada"
            )
        
        # Verificar que el usuario no sea el autor del evento
        if str(publicacion.id_autor) == str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No puedes inscribirte en tu propio evento"
            )
        
        # Verificar que no esté ya inscrito
        from models.inscripcion import Inscripcion
        inscripcion_existente = db.query(Inscripcion).filter(
            Inscripcion.id_usuario == current_user.id,
            Inscripcion.id_publicacion == post_id
        ).first()
        
        if inscripcion_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya estás inscrito en este evento"
            )
        
        # Crear la inscripción
        nueva_inscripcion = Inscripcion(
            id_usuario=current_user.id,
            id_publicacion=post_id,
            estado_asistencia="inscrito"
        )
        
        db.add(nueva_inscripcion)
        db.commit()
        
        return {
            "message": "Inscripción exitosa",
            "inscripcion_id": str(nueva_inscripcion.id_usuario) + "_" + str(nueva_inscripcion.id_publicacion)
        }
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de publicación inválido"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al inscribirse en el evento: {str(e)}"
        )

@router.delete("/{post_id}/desinscribirse", summary="Desinscribirse de un evento")
def desinscribirse_evento(
    post_id: str,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Desinscribe al usuario actual de un evento específico
    """
    try:
        # Validar que el post_id sea un UUID válido
        uuid.UUID(post_id)
        
        # Verificar que la publicación existe
        publicacion = db.query(Publicacion).filter(Publicacion.id == post_id).first()
        if not publicacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Publicación no encontrada"
            )
        
        # Buscar la inscripción
        from models.inscripcion import Inscripcion
        inscripcion = db.query(Inscripcion).filter(
            Inscripcion.id_usuario == current_user.id,
            Inscripcion.id_publicacion == post_id
        ).first()
        
        if not inscripcion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No estás inscrito en este evento"
            )
        
        # Eliminar la inscripción
        db.delete(inscripcion)
        db.commit()
        
        return {"message": "Desinscripción exitosa"}
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de publicación inválido"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al desinscribirse del evento: {str(e)}"
        )
