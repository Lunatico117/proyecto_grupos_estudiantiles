# Maneja operaciones generales de usuarios, aparte de login/registro.
# Aquí se gestionan cosas como consultar, actualizar, eliminar o cambiar roles de usuarios.
from src.model.usuario import Usuario
from src.services.firebase import FirebaseService

class UsuarioViewModel:
    # ViewModel para manejar operaciones generales de usuarios con Firebase.
    
    def __init__(self, service=None):
        # Si se pasa un servicio de Firebase externo (por ejemplo, para pruebas), se usa ese.
        # Si no, se crea uno nuevo.
        self.service = service if service else FirebaseService()
        # Define la ruta donde están almacenados los usuarios dentro de Firebase.
        self.ruta_usuarios = "usuarios"

    # Busca y obtiene un usuario en Firebase usando su correo.
    # Retorna un objeto Usuario si lo encuentra, o None si no existe.
    def obtener_usuario(self, correo):
        # Firebase no permite ciertos caracteres en las rutas, por eso se reemplazan.
        correo_key = correo.replace('@', '_at_').replace('.', '_dot_')
        ruta_usuario = f"{self.ruta_usuarios}/{correo_key}"
        # Se obtienen los datos del usuario desde Firebase.
        data = self.service.obtener_datos(ruta_usuario)
        if not data:
            # Si no hay datos, el usuario no existe.
            return None
        # Se devuelve un objeto Usuario usando los datos obtenidos.
        return Usuario(**data)

    # Actualiza los datos de un usuario. Solo se cambian los campos enviados.
    def actualizar_usuario(self, correo, nombre_completo=None, password=None, carrera=None, descripcion_personal=None):
        # Primero obtenemos el usuario para verificar que existe.
        usuario = self.obtener_usuario(correo)
        if not usuario:
            return {'success': False, 'error': 'Usuario no encontrado.'}

        # Si se pasó un nombre completo nuevo, se actualiza.
        if nombre_completo:
            usuario.nombre_completo = nombre_completo
        # Si se pasó una contraseña nueva, se actualiza.
        if password:
            usuario.contraseña = password
        # Si se pasó una carrera nueva, se actualiza.
        if carrera:
            usuario.carrera = carrera
        # Si se pasó una descripción personal nueva, se actualiza.
        if descripcion_personal:
            usuario.descripcion_personal = descripcion_personal

        # Se vuelve a generar la clave del correo.
        correo_key = correo.replace('@', '_at_').replace('.', '_dot_')
        ruta_usuario = f"{self.ruta_usuarios}/{correo_key}"
        # Se guarda el usuario actualizado en Firebase.
        self.service.actualizar_datos(ruta_usuario, usuario.to_dict())
        return {'success': True, 'mensaje': 'Usuario actualizado correctamente.'}

    # Elimina completamente un usuario del sistema y lo quita de todos los grupos donde esté inscrito (de Firebase).
    def eliminar_usuario(self, correo):
        correo_key = correo.replace('@', '_at_').replace('.', '_dot_')
        ruta_usuario = f"{self.ruta_usuarios}/{correo_key}"

        from src.viewmodel.grupos_viewmodel import GruposViewModel
        grupos_vm = GruposViewModel(self.service)

        todos_los_grupos = grupos_vm.listar_grupos()

        for grupo in todos_los_grupos:
            if correo in grupo["integrantes"]:
                # Caso: único organizador → eliminar grupo
                if correo in grupo["organizadores"] and len(grupo["organizadores"]) == 1:
                    grupos_vm.eliminar_grupo(grupo["id_grupo"])
                else:
                    # Caso: hay otros organizadores → solo remover al usuario
                    if correo in grupo["integrantes"]:
                        grupo["integrantes"].remove(correo)
                    if correo in grupo["organizadores"]:
                        grupo["organizadores"].remove(correo)
                    self.service.actualizar_datos(f"grupos/{grupo['id_grupo']}", grupo)

        # Finalmente, eliminar usuario de Firebase
        self.service.eliminar_datos(ruta_usuario)

        return {'success': True, 'mensaje': f'Usuario {correo} eliminado y removido de sus grupos.'}


    # Devuelve una lista con todos los grupos a los que pertenece un usuario.
    def consultar_grupos_usuario(self, correo):
        # Se importa el ViewModel de grupos (aquí dentro para evitar importaciones circulares).
        from src.viewmodel.grupos_viewmodel import GruposViewModel
        grupos_vm = GruposViewModel(self.service)
        # Se listan todos los grupos existentes.
        todos_los_grupos = grupos_vm.listar_grupos()
        # Se filtran los grupos donde el correo está en la lista de integrantes.
        grupos_usuario = [g for g in todos_los_grupos if correo in g['integrantes']]
        return grupos_usuario

    # Verifica si un usuario es organizador de un grupo específico.
    def es_organizador_de_grupo(self, correo, id_grupo):
        from src.viewmodel.grupos_viewmodel import GruposViewModel
        grupos_vm = GruposViewModel(self.service)
        # Se obtiene el grupo a partir del ID.
        grupo = grupos_vm.obtener_grupo(id_grupo)
        if not grupo:
            # Si no existe, se retorna False.
            return False
        # Devuelve True si el correo está en la lista de organizadores.
        return correo in grupo.organizadores

    # Cambia el rol de un usuario dentro de un grupo.
    # Ejemplo: de 'miembro' a 'organizador' o viceversa.
    def cambiar_rol_usuario(self, correo_usuario, id_grupo, nuevo_rol):
        from src.viewmodel.grupos_viewmodel import GruposViewModel
        grupos_vm = GruposViewModel(self.service)

        # Se busca el grupo por ID.
        grupo = grupos_vm.obtener_grupo(id_grupo)
        if not grupo:
            return {'success': False, 'error': 'Grupo no encontrado.'}

        # Verificamos que el usuario esté dentro de los integrantes del grupo.
        if correo_usuario not in grupo.integrantes:
            return {'success': False, 'error': 'El usuario no pertenece al grupo.'}

        # Si el nuevo rol es "organizador", lo añadimos si aún no está.
        if nuevo_rol == 'organizador':
            if correo_usuario not in grupo.organizadores:
                grupo.organizadores.append(correo_usuario)

        # Si el nuevo rol es "miembro", lo removemos de la lista de organizadores.
        elif nuevo_rol == 'miembro':
            if correo_usuario in grupo.organizadores:
                grupo.organizadores.remove(correo_usuario)

        # Si el rol no es válido, se lanza un error.
        else:
            return {'success': False, 'error': 'Rol inválido.'}

        # Guardamos los cambios del grupo en Firebase.
        self.service.actualizar_datos(f"grupos/{grupo.id_grupo}", grupo.to_dict())
        return {'success': True, 'mensaje': f'Rol del usuario actualizado a {nuevo_rol}.'}
