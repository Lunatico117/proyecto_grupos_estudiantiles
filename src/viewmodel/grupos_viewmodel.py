# Maneja las operaciones entre usuarios y grupos.

# Importamos la clase Grupo (nuestro modelo de datos de grupos)
# y FirebaseService (para conectarnos y manipular Firebase)
from datetime import datetime

from src.model.evento import Evento
from src.model.grupo import Grupo
from src.services.firebase import FirebaseService
from src.viewmodel.usuarios_viewmodel import UsuarioViewModel  


class GruposViewModel:
    # Clase que maneja la lógica de los grupos y su conexión con Firebase

    def __init__(self, service=None):
        # Si nos pasan un servicio de Firebase, lo usamos; si no, creamos uno nuevo
        # Esto permite inyectar un servicio diferente para pruebas o futuras mejoras
        self.service = service if service else FirebaseService()
        # Definimos la "carpeta" principal en Firebase donde estarán todos los grupos
        self.ruta_grupos = "grupos"

    # --- CRUD Básico: Crear, Leer, Actualizar, Eliminar ---

    def crear_grupo(self, nombre, descripcion, categoria, organizadores):
        # Crea un nuevo grupo y lo guarda en Firebase
        
        # Creamos un objeto Grupo en Python
        grupo = Grupo(
            nombre=nombre, 
            descripcion=descripcion,
            categoria=categoria, 
            organizadores=organizadores
        )
        # Definimos la ruta en Firebase donde guardaremos este grupo
        ruta = f"{self.ruta_grupos}/{grupo.id_grupo}"
        # Guardamos los datos del grupo en Firebase como diccionario
        self.service.guardar_datos(ruta, grupo.to_dict())
        # Retornamos el diccionario para usarlo fácilmente en el frontend o más lógica
        return grupo.to_dict()
    
    def obtener_grupo(self, id_grupo):
        datos = self.service.obtener_datos(f"{self.ruta_grupos}/{id_grupo}") or {}
        if datos:
            grupo = Grupo.from_dict(datos)
            self._limpiar_eventos_vencidos(id_grupo, grupo)
            return grupo
        return None

    def guardar_grupo_dict(self, id_grupo, grupo_dict):
        # actualiza todo el documento
        self.service.actualizar_datos(f"{self.ruta_grupos}/{id_grupo}", grupo_dict)

    def listar_grupos(self):
        # Lista todos los grupos guardados en Firebase
        
        # Obtenemos todos los datos de la carpeta 'grupos'
        data = self.service.obtener_datos(self.ruta_grupos)
        # Si no hay grupos, devolvemos lista vacía
        if not data:
            return []
        # Convertimos cada diccionario a objeto Grupo y luego a dict (para frontend)
        return [Grupo(**info).to_dict() for info in data.values()]

    def actualizar_grupo(self, id_grupo, nombre=None, descripcion=None, categoria=None):
        # Actualiza la información de un grupo existente
        
        # Primero obtenemos el grupo desde Firebase
        grupo = self.obtener_grupo(id_grupo)
        # Si no existe, devolvemos False indicando que no se pudo actualizar
        if not grupo:
            return False
        # Llamamos al método del modelo para actualizar la info
        grupo.actualizar_info(nombre, descripcion, categoria)
        # Guardamos los cambios en Firebase
        self.service.actualizar_datos(f"{self.ruta_grupos}/{id_grupo}", grupo.to_dict())
        return True

    def eliminar_grupo(self, id_grupo):
        # Elimina un grupo    

        # Obtener el grupo a eliminar
        grupo = self.obtener_grupo(id_grupo)
        if not grupo:
            return {'success': False, 'error': 'Grupo no encontrado.'}

        # Eliminar el grupo de Firebase
        self.service.eliminar_datos(f"{self.ruta_grupos}/{id_grupo}")
        return {'success': True, 'mensaje': f'Grupo {grupo.nombre} eliminado correctamente.'}

    # --- Gestión de integrantes del grupo ---

    def agregar_integrante(self, id_grupo, usuario):
        # Agrega un usuario a la lista de integrantes de un grupo
        
        # Obtenemos el grupo primero
        grupo = self.obtener_grupo(id_grupo)
        if not grupo:  # Si no existe, devolvemos False
            return False
        # Intentamos agregar el usuario al grupo usando método de la clase Grupo
        if grupo.agregar_integrante(usuario):
            # Si se agregó correctamente, actualizamos Firebase
            self.service.actualizar_datos(f"{self.ruta_grupos}/{id_grupo}", grupo.to_dict())
            return True
        # Si el usuario ya estaba, devolvemos False
        return False

    def remover_integrante(self, id_grupo, usuario):
        # Elimina un usuario de la lista de integrantes de un grupo
       
        # Obtenemos el grupo
        grupo = self.obtener_grupo(id_grupo)
        if not grupo:
            return False
        # Intentamos remover el usuario usando método de la clase Grupo
        if grupo.remover_integrante(usuario):
            # Actualizamos Firebase con la nueva lista de integrantes
            self.service.actualizar_datos(f"{self.ruta_grupos}/{id_grupo}", grupo.to_dict())
            return True
        return False

    def listar_grupos_con_usuarios(self):
        # Retorna una lista de grupos, pero cada uno con los nombres de sus integrantes.
        
        # Obtenemos todos los grupos desde Firebase
        grupos = self.listar_grupos()

        # Para cada grupo, agregamos un nuevo campo 'nombres_integrantes'
        for g in grupos:
            nombres = []

            # Recorremos los correos de los integrantes
            for correo in g.get("integrantes", []):
                # Importación solo dentro del método para evitar circularidad
                from src.viewmodel.usuarios_viewmodel import UsuarioViewModel
                # Buscamos al usuario en Firebase usando UsuarioViewModel
                usuario = UsuarioViewModel(self.service).obtener_usuario(correo)

                # Si el usuario existe, añadimos su nombre; si no, dejamos el correo
                if usuario:
                    nombres.append(usuario.nombre)
                else:
                    nombres.append(correo)

            # Agregamos la nueva lista al grupo
            g["nombres_integrantes"] = nombres

        # Devolvemos la lista de grupos con los nombres incluidos
        return grupos

    def _parsear_fecha_evento(self, evento):
        fecha = evento.get("fecha")
        hora = (evento.get("hora") or "00:00").strip()
        if not fecha:
            return None

        intentos = (
            (f"{fecha} {hora}", "%Y-%m-%d %H:%M"),
            (f"{fecha} {hora}", "%Y-%m-%d %H:%M:%S"),
            (fecha, "%Y-%m-%d"),
        )
        for valor, formato in intentos:
            try:
                return datetime.strptime(valor, formato)
            except ValueError:
                continue
        return None

    def _limpiar_eventos_vencidos(self, id_grupo, grupo):
        if not grupo or not getattr(grupo, "eventos", None):
            return

        ahora = datetime.now()
        vigentes = []
        for evento in grupo.eventos:
            dt_evento = self._parsear_fecha_evento(evento)
            if dt_evento and dt_evento < ahora:
                continue
            vigentes.append(evento)

        if len(vigentes) != len(grupo.eventos):
            grupo.eventos = vigentes
            self.guardar_grupo_dict(id_grupo, grupo.to_dict())

    def crear_evento(self, id_grupo, fecha, hora, descripcion, creado_por_email):
        """
        Crea un evento y lo añade al arreglo 'eventos' dentro del grupo en Firebase.
        """
        grupo = self.obtener_grupo(id_grupo)
        if not grupo:
            return {"success": False, "error": "Grupo no encontrado"}
        # Validación simple (puedes expandir)
        if not (fecha and hora and descripcion):
            return {"success": False, "error": "Datos incompletos"}

        # Intentar obtener nombre del creador
        try:
            usuario_vm = UsuarioViewModel(self.service)
            usuario = usuario_vm.obtener_usuario(creado_por_email)
            nombre_creador = usuario.nombre if usuario else None
        except Exception:
            nombre_creador = None

        evento = Evento(fecha=fecha, hora=hora, descripcion=descripcion,
                        creado_por_email=creado_por_email,
                        creado_por_nombre=nombre_creador)

        # Añadir al grupo y actualizar en Firebase
        grupo.agregar_evento(evento.to_dict())
        self.guardar_grupo_dict(id_grupo, grupo.to_dict())
        return {"success": True, "evento": evento.to_dict()}

    def obtener_eventos_por_grupo(self, id_grupo):
        grupo = self.obtener_grupo(id_grupo)
        if not grupo:
            return []
        # devolver ordenados por fecha+hora asc (opcional)
        try:
            eventos = sorted(grupo.eventos, key=lambda e: (e.get("fecha",""), e.get("hora","")))
        except Exception:
            eventos = grupo.eventos or []
        return eventos

    def obtener_eventos_por_usuario(self, correo_usuario):
        """
        Recorre todos los grupos y devuelve los eventos de aquellos donde el usuario es integrante.
        Devuelve lista de dicts con un campo adicional 'grupo_id' y 'grupo_nombre'.
        """
        grupos = self.service.obtener_datos(self.ruta_grupos) or {}
        resultados = []
        for gid, gdict in grupos.items():
            if not gdict:
                continue

            grupo = Grupo.from_dict(gdict)
            self._limpiar_eventos_vencidos(gid, grupo)

            if correo_usuario in grupo.integrantes:
                for e in grupo.eventos:
                    evt = e.copy()
                    evt["grupo_id"] = getattr(grupo, "id_grupo", gid)
                    evt["grupo_nombre"] = getattr(grupo, "nombre", "Sin nombre")
                    resultados.append(evt)
        # opcional: ordenar por fecha+hora asc
        try:
            resultados = sorted(resultados, key=lambda e: (e.get("fecha",""), e.get("hora","")))
        except Exception:
            pass
        return resultados

    def eliminar_evento(self, id_grupo, id_evento):
        grupo = self.obtener_grupo(id_grupo)
        if not grupo:
            return {"success": False, "error": "Grupo no encontrado"}
        eliminado = grupo.eliminar_evento_por_id(id_evento)
        if eliminado:
            self.guardar_grupo_dict(id_grupo, grupo.to_dict())
            return {"success": True}
        return {"success": False, "error": "Evento no encontrado"}
