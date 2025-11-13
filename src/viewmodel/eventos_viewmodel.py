from src.model.evento import Evento
from src.model.grupo import Grupo
from src.services.firebase_global import firebase_global
from src.viewmodel.usuarios_viewmodel import UsuarioViewModel

class EventosViewModel:
    def __init__(self, service=None):
        self.service = service if service else firebase_global
        self.ruta_grupos = "grupos"

    def _obtener_grupo(self, id_grupo):
        data = self.service.obtener_datos(f"{self.ruta_grupos}/{id_grupo}")
        return Grupo.from_dict(data) if data else None

    def _guardar_grupo(self, id_grupo, grupo_dict):
        self.service.actualizar_datos(f"{self.ruta_grupos}/{id_grupo}", grupo_dict)

    def crear_evento(self, id_grupo, fecha, hora, descripcion, creado_por_email):
        grupo = self._obtener_grupo(id_grupo)
        if not grupo:
            return {"success": False, "error": "Grupo no encontrado"}

        try:
            usuario_vm = UsuarioViewModel(self.service)
            usuario = usuario_vm.obtener_usuario(creado_por_email)
            nombre_creador = usuario.nombre if usuario else None
        except Exception:
            nombre_creador = None

        evento = Evento(fecha, hora, descripcion, creado_por_email, nombre_creador)
        grupo.agregar_evento(evento.to_dict())
        self._guardar_grupo(id_grupo, grupo.to_dict())
        return {"success": True, "evento": evento.to_dict()}

    def obtener_eventos_por_grupo(self, id_grupo):
        grupo = self._obtener_grupo(id_grupo)
        if not grupo:
            return []
        return sorted(grupo.eventos, key=lambda e: (e.get("fecha", ""), e.get("hora", "")))

    def obtener_eventos_por_usuario(self, correo):
        grupos = self.service.obtener_datos(self.ruta_grupos) or {}
        eventos_usuario = []
        for gid, gdata in grupos.items():
            if correo in gdata.get("integrantes", []):
                for e in gdata.get("eventos", []):
                    ev = e.copy()
                    ev["grupo_id"] = gid
                    ev["grupo_nombre"] = gdata.get("nombre", "Sin nombre")
                    eventos_usuario.append(ev)
        return sorted(eventos_usuario, key=lambda e: (e.get("fecha", ""), e.get("hora", "")))

    def eliminar_evento(self, id_grupo, id_evento):
        grupo = self._obtener_grupo(id_grupo)
        if not grupo:
            return {"success": False, "error": "Grupo no encontrado"}
        eliminado = grupo.eliminar_evento_por_id(id_evento)
        if eliminado:
            self._guardar_grupo(id_grupo, grupo.to_dict())
            return {"success": True}
        return {"success": False, "error": "Evento no encontrado"}
