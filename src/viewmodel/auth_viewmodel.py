# maneja inicio de sesión, registro y validación.

from src.model.usuario import Usuario
from src.services.firebase import FirebaseService

class UsuarioViewModel:
    def __init__(self, service=None):
        # El servicio de Firebase para acceso a datos
        self.service = service if service else FirebaseService()

    def registrar_usuario(self, nombre, correo, password, carrera):
        # 1. Validar correo institucional
        if not Usuario.es_correo_valido(correo):
            return {'success': False, 'error': 'El correo debe ser institucional @unal.edu.co'}

        # 2. Crear clave 'segura' para el usuario en la BD
        correo_key = correo.replace('@', '_at_').replace('.', '_dot_')
        ruta_usuario = f"usuarios/{correo_key}"

        # 3. Verificar si el usuario ya existe
        existente = self.service.obtener_datos(ruta_usuario)
        if existente:
            return {'success': False, 'error': 'Ese correo ya está registrado.'}

        # 4. Crear y guardar el usuario
        usuario = Usuario(nombre=nombre, correo=correo, password=password, carrera=carrera)
        self.service.guardar_datos(ruta_usuario, usuario.to_dict())
        return {'success': True, 'mensaje': f'Usuario {nombre} registrado correctamente.'}

    def iniciar_sesion(self, correo, password):
        # 1. Buscar usuario en BD
        correo_key = correo.replace('@', '_at_').replace('.', '_dot_')
        ruta_usuario = f"usuarios/{correo_key}"
        usuario_data = self.service.obtener_datos(ruta_usuario)

        if not usuario_data:
            return {'success': False, 'error': 'Usuario no encontrado.'}
        # 2. Validar la contraseña (¡mejor hashearla en producción!)
        if usuario_data.get('password') != password:
            return {'success': False, 'error': 'Contraseña incorrecta.'}

        return {'success': True, 'mensaje': 'Inicio de sesión exitoso.', 'usuario': usuario_data}

    def validar_datos(self, nombre, correo, password, carrera):
        # Validaciones básicas que puedes expandir
        if not nombre or not correo or not password or not carrera:
            return {'success': False, 'error': 'Todos los campos son obligatorios.'}
        if not Usuario.es_correo_valido(correo):
            return {'success': False, 'error': 'Correo institucional incorrecto.'}
        if len(password) < 6:
            return {'success': False, 'error': 'La contraseña debe tener al menos 6 caracteres.'}
        return {'success': True}
