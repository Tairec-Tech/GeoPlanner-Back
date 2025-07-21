-- =============================================================================
-- Script de Creación de Base de Datos para GeoPlanner
-- Base de Datos: PostgreSQL
-- Versión: 1.0
-- Descripción: Este script crea todas las tablas, tipos, relaciones e
--              índices necesarios para el funcionamiento de la aplicación
--              GeoPlanner.
-- =============================================================================

-- Habilitar la extensión para generar UUIDs. Ejecutar una sola vez por base de datos.
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =============================================================================
-- SECCIÓN 1: DEFINICIÓN DE TIPOS ENUMERADOS (ENUMS)
-- Los ENUMs ayudan a restringir los valores de una columna a un conjunto fijo,
-- mejorando la integridad de los datos.
-- =============================================================================

CREATE TYPE TIPO_GENERO AS ENUM ('Masculino', 'Femenino', 'Otro');
CREATE TYPE TIPO_PUBLICACION AS ENUM ('Deporte', 'Social', 'Estudio', 'Cultural', 'Otro');
CREATE TYPE TIPO_PRIVACIDAD AS ENUM ('publica', 'amigos', 'privada');
CREATE TYPE ESTADO_PUBLICACION AS ENUM ('vigente', 'finalizado', 'cancelado');
CREATE TYPE ESTADO_ASISTENCIA AS ENUM ('inscrito', 'asistio', 'no_asistio');
CREATE TYPE ESTADO_AMISTAD AS ENUM ('pendiente', 'aceptada', 'rechazada');

-- =============================================================================
-- SECCIÓN 2: CREACIÓN DE TABLAS
-- Se crean las tablas en un orden que respeta las dependencias de llaves foráneas.
-- =============================================================================

-- Tabla de Usuarios: Almacena la información de cada usuario registrado.
CREATE TABLE Usuarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre_usuario VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    fecha_nacimiento DATE NOT NULL,
    genero TIPO_GENERO,
    foto_perfil_url TEXT,
    biografia VARCHAR(160),
    latitud NUMERIC(9, 6),
    longitud NUMERIC(9, 6),
    ciudad VARCHAR(100),
    pais VARCHAR(100),
    tema_preferido VARCHAR(50) DEFAULT 'default',
    verificado BOOLEAN DEFAULT FALSE,
    fecha_creacion TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE Usuarios IS 'Almacena la información de cada usuario registrado en la plataforma.';
COMMENT ON COLUMN Usuarios.password_hash IS 'Contraseña hasheada del usuario para seguridad.';

-- Tabla de Publicaciones: Contiene todos los eventos creados por los usuarios.
CREATE TABLE Publicaciones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_autor UUID NOT NULL REFERENCES Usuarios(id) ON DELETE CASCADE,
    texto TEXT NOT NULL,
    tipo TIPO_PUBLICACION NOT NULL,
    fecha_evento TIMESTAMPTZ NOT NULL,
    privacidad TIPO_PRIVACIDAD NOT NULL DEFAULT 'publica',
    media_url TEXT,
    terminos_adicionales TEXT,
    estado ESTADO_PUBLICACION NOT NULL DEFAULT 'vigente',
    fecha_creacion TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE Publicaciones IS 'Contiene todos los eventos o actividades creadas por los usuarios.';
COMMENT ON COLUMN Publicaciones.id_autor IS 'Llave foránea que referencia al autor del evento en la tabla Usuarios.';

-- Tabla de Rutas: Almacena los puntos geográficos para cada publicación.
-- Se separa para manejar correctamente las rutas de múltiples puntos (relación uno a muchos).
CREATE TABLE Rutas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_publicacion UUID NOT NULL REFERENCES Publicaciones(id) ON DELETE CASCADE,
    latitud NUMERIC(9, 6) NOT NULL,
    longitud NUMERIC(9, 6) NOT NULL,
    etiqueta VARCHAR(255),
    orden INTEGER NOT NULL -- Para mantener el orden de los puntos en una ruta
);

COMMENT ON TABLE Rutas IS 'Almacena los puntos geográficos de una publicación. Permite rutas multipunto.';
COMMENT ON COLUMN Rutas.orden IS 'Define la secuencia de los puntos en una ruta múltiple.';

-- Tabla de Comentarios: Almacena los comentarios hechos en las publicaciones.
CREATE TABLE Comentarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_publicacion UUID NOT NULL REFERENCES Publicaciones(id) ON DELETE CASCADE,
    id_autor UUID NOT NULL REFERENCES Usuarios(id) ON DELETE CASCADE,
    texto TEXT NOT NULL,
    fecha_creacion TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE Comentarios IS 'Almacena los comentarios de los usuarios en las publicaciones.';

-- Tabla de Likes: Registra los "me gusta" de los usuarios en las publicaciones.
CREATE TABLE Likes (
    id_usuario UUID NOT NULL REFERENCES Usuarios(id) ON DELETE CASCADE,
    id_publicacion UUID NOT NULL REFERENCES Publicaciones(id) ON DELETE CASCADE,
    fecha_creacion TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_usuario, id_publicacion) -- Un usuario solo puede dar un like por publicación
);

COMMENT ON TABLE Likes IS 'Tabla de unión para registrar los "me gusta" en las publicaciones.';

-- Tabla de Inscripciones: Registra la participación de un usuario en un evento.
CREATE TABLE Inscripciones (
    id_usuario UUID NOT NULL REFERENCES Usuarios(id) ON DELETE CASCADE,
    id_publicacion UUID NOT NULL REFERENCES Publicaciones(id) ON DELETE CASCADE,
    fecha_inscripcion TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    estado_asistencia ESTADO_ASISTENCIA NOT NULL DEFAULT 'inscrito',
    PRIMARY KEY (id_usuario, id_publicacion) -- Un usuario solo puede inscribirse una vez por evento
);

COMMENT ON TABLE Inscripciones IS 'Registra la inscripción de un usuario a un evento (publicación).';

-- Tabla de Amistades: Modela las relaciones de amistad entre usuarios.
CREATE TABLE Amistades (
    id_usuario1 UUID NOT NULL REFERENCES Usuarios(id) ON DELETE CASCADE,
    id_usuario2 UUID NOT NULL REFERENCES Usuarios(id) ON DELETE CASCADE,
    estado ESTADO_AMISTAD NOT NULL,
    id_usuario_accion UUID NOT NULL REFERENCES Usuarios(id) ON DELETE CASCADE,
    fecha_creacion TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_usuario1, id_usuario2),
    CONSTRAINT chk_no_self_friendship CHECK (id_usuario1 <> id_usuario2),
    CONSTRAINT chk_user_order CHECK (id_usuario1 < id_usuario2) -- Evita duplicados (A,B) y (B,A)
);

COMMENT ON TABLE Amistades IS 'Modela las relaciones de amistad entre dos usuarios.';
COMMENT ON COLUMN Amistades.id_usuario_accion IS 'El usuario que envió la solicitud o realizó la última acción.';
COMMENT ON CONSTRAINT chk_user_order ON Amistades IS 'Asegura que el id del usuario1 sea siempre menor que el del usuario2 para evitar registros duplicados.';

-- Tabla de EventosGuardados: Permite a los usuarios guardar publicaciones de interés.
CREATE TABLE EventosGuardados (
    id_usuario UUID NOT NULL REFERENCES Usuarios(id) ON DELETE CASCADE,
    id_publicacion UUID NOT NULL REFERENCES Publicaciones(id) ON DELETE CASCADE,
    fecha_guardado TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_usuario, id_publicacion)
);

COMMENT ON TABLE EventosGuardados IS 'Permite a los usuarios guardar publicaciones para verlas más tarde.';

-- Tabla de ActividadesAgenda: Almacena las actividades privadas de la agenda de un usuario.
CREATE TABLE ActividadesAgenda (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_usuario UUID NOT NULL REFERENCES Usuarios(id) ON DELETE CASCADE,
    titulo VARCHAR(255) NOT NULL,
    descripcion TEXT,
    fecha_actividad TIMESTAMPTZ NOT NULL,
    fecha_creacion TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE ActividadesAgenda IS 'Almacena las actividades privadas de la agenda personal de cada usuario.';

-- =============================================================================
-- SECCIÓN 3: CREACIÓN DE ÍNDICES
-- Los índices son cruciales para acelerar las operaciones de búsqueda y lectura.
-- =============================================================================

-- Índices para la tabla Publicaciones
CREATE INDEX idx_publicaciones_id_autor ON Publicaciones(id_autor);
CREATE INDEX idx_publicaciones_fecha_evento ON Publicaciones(fecha_evento DESC);

-- Índices para la tabla Rutas
CREATE INDEX idx_rutas_id_publicacion ON Rutas(id_publicacion);

-- Índices para la tabla Comentarios
CREATE INDEX idx_comentarios_id_publicacion ON Comentarios(id_publicacion);
CREATE INDEX idx_comentarios_id_autor ON Comentarios(id_autor);

-- Índices para la tabla Amistades (para buscar amigos de un usuario)
CREATE INDEX idx_amistades_id_usuario2 ON Amistades(id_usuario2);

-- Índice para la tabla ActividadesAgenda
CREATE INDEX idx_actividades_agenda_id_usuario ON ActividadesAgenda(id_usuario);
CREATE INDEX idx_actividades_agenda_fecha ON ActividadesAgenda(fecha_actividad);


-- =============================================================================
-- Fin del Script
-- =============================================================================
