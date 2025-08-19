import enum

class TipoGeneroEnum(enum.Enum):
    Masculino = 'Masculino'
    Femenino = 'Femenino'
    Otro = 'Otro'

class TipoPublicacionEnum(enum.Enum):
    Deporte = 'Deporte'
    Social = 'Social'
    Estudio = 'Estudio'
    Cultural = 'Cultural'
    Otro = 'Otro'

class TipoPrivacidadEnum(enum.Enum):
    publica = 'publica'
    amigos = 'amigos'
    privada = 'privada'

class EstadoPublicacionEnum(enum.Enum):
    vigente = 'vigente'
    finalizado = 'finalizado'
    cancelado = 'cancelado'

class EstadoAsistenciaEnum(enum.Enum):
    inscrito = 'inscrito'
    asistio = 'asistio'
    no_asistio = 'no_asistio'

class EstadoAmistadEnum(enum.Enum):
    pendiente = 'pendiente'
    aceptada = 'aceptada'
    rechazada = 'rechazada'
