# Maneja las operaciones entre usuarios y grupos.

# Importamos la clase Grupo (nuestro modelo de datos de grupos)
# y FirebaseService (para conectarnos y manipular Firebase)
from src.model.grupo import Grupo
from src.services.firebase import FirebaseService


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
        # Obtiene un grupo desde Firebase usando su ID
        
        # Pedimos los datos de Firebase
        data = self.service.obtener_datos(f"{self.ruta_grupos}/{id_grupo}")
        # Si no existe el grupo, devolvemos None
        if not data:
            return None
        # Convertimos el diccionario de Firebase de vuelta a un objeto Grupo
        return Grupo(**data)

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
