import uuid
from datetime import datetime

class Evento:
    """Modelo simple de Evento"""

    def __init__(self, fecha, hora, descripcion, creado_por_email, creado_por_nombre=None, id_evento=None, creado_en_iso=None):
        self.id = id_evento if id_evento else str(uuid.uuid4())
        self.fecha = fecha
        self.hora = hora
        self.descripcion = descripcion
        self.creado_por_email = creado_por_email
        self.creado_por_nombre = creado_por_nombre
        self.creado_en_iso = creado_en_iso if creado_en_iso else datetime.utcnow().isoformat()

    def to_dict(self):
        return {
            "id": self.id,
            "fecha": self.fecha,
            "hora": self.hora,
            "descripcion": self.descripcion,
            "creado_por_email": self.creado_por_email,
            "creado_por_nombre": self.creado_por_nombre,
            "creado_en_iso": self.creado_en_iso,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            fecha=d.get("fecha"),
            hora=d.get("hora"),
            descripcion=d.get("descripcion"),
            creado_por_email=d.get("creado_por_email"),
            creado_por_nombre=d.get("creado_por_nombre"),
            id_evento=d.get("id"),
            creado_en_iso=d.get("creado_en_iso"),
        )
