# auth_viewmodel.py
# Maneja inicio de sesión, registro y validación de usuarios

from src.model.usuario import Usuario
from src.services.firebase import FirebaseService
from src.utils.validaciones import es_correo_valido  # Función que valida correos institucionales


class UsuarioAuthViewModel:
    """
    ViewModel encargado de la autenticación de usuarios:
    - Registro
    - Inicio de sesión
    - Validaciones básicas
    """

    def __init__(self, service=None):
        # Inicializa el servicio de Firebase. Permite inyectar un servicio diferente para pruebas.
        self.service = service if service else FirebaseService()

    def registrar_usuario(self, nombre, correo, password, carrera):
        """
        Registra un nuevo usuario en Firebase
        """
        # 1. Validar correo institucional
        if not es_correo_valido(correo):
            return {'success': False, 'error': 'El correo debe ser institucional @unal.edu.co'}

        # 2. Crear clave 'segura' para almacenar usuario en Firebase
        correo_key = correo.replace('@', '_at_').replace('.', '_dot_')
        ruta_usuario = f"usuarios/{correo_key}"

        # 3. Verificar si el usuario ya existe
        existente = self.service.obtener_datos(ruta_usuario)
        if existente:
            return {'success': False, 'error': 'Ese correo ya está registrado.'}

        # 4. Crear usuario usando el método de clase 'crear_usuario' del modelo Usuario
        # Esto genera automáticamente un id_usuario único y valida el correo
        usuario = Usuario.crear_usuario(
            nombre_completo=nombre,
            correo=correo,
            contraseña=password,
            carrera=carrera
        )

        # 5. Guardar en Firebase
        self.service.guardar_datos(ruta_usuario, usuario.to_dict())

        return {'success': True, 'mensaje': f'Usuario {nombre} registrado correctamente.'}

    def iniciar_sesion(self, correo, password):
        """
        Valida el inicio de sesión de un usuario
        """
        # 1. Generar la clave para buscar al usuario
        correo_key = correo.replace('@', '_at_').replace('.', '_dot_')
        ruta_usuario = f"usuarios/{correo_key}"

        # 2. Obtener datos del usuario en Firebase
        usuario_data = self.service.obtener_datos(ruta_usuario)
        if not usuario_data:
            return {'success': False, 'error': 'Usuario no encontrado.'}

        # 3. Validar contraseña (campo 'contraseña' según modelo Usuario)
        if usuario_data.get('contraseña') != password:
            return {'success': False, 'error': 'Contraseña incorrecta.'}

        return {'success': True, 'mensaje': 'Inicio de sesión exitoso.', 'usuario': usuario_data}

    def validar_datos(self, nombre, correo, password, carrera):
        """
        Validaciones básicas antes de registrar un usuario
        """
        if not nombre or not correo or not password or not carrera:
            return {'success': False, 'error': 'Todos los campos son obligatorios.'}

        if not es_correo_valido(correo):
            return {'success': False, 'error': 'Correo institucional incorrecto.'}

        if len(password) < 6:
            return {'success': False, 'error': 'La contraseña debe tener al menos 6 caracteres.'}

        return {'success': True}
