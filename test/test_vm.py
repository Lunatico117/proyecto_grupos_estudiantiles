# Se prueba con el comando "python -m test.test_vm" en terminal 
# test_vm.py
# Este archivo prueba de manera sencilla el funcionamiento de los modelos y viewmodels
# No cubre todos los casos, solo los básicos para ver que todo esté conectado correctamente.

import os
from src.model.usuario import Usuario
from src.model.grupo import Grupo
from src.viewmodel.usuarios_viewmodel import UsuarioViewModel
from src.viewmodel.grupos_viewmodel import GruposViewModel
from src.services.firebase import FirebaseService

# --- Configuración de prueba ---
# Para estas pruebas puedes usar un servicio de Firebase real o un "mock"
# Aquí usaremos un servicio real, asumiendo que ya configuraste tus variables de entorno
service = FirebaseService()

# --- Prueba de Usuario ---
def test_usuario_vm():
    print("=== Test UsuarioViewModel ===")
    
    # Creamos un usuario de prueba usando la clase Usuario
    usuario_prueba = Usuario(
        id_usuario="guapeton",
        nombre_completo="Nestor",
        correo="Nestor@test.com",
        contraseña="1234",
        carrera="Medicina"
    )

    print("Usuario creado:", usuario_prueba)

    # Inicializamos el ViewModel de usuarios
    usuario_vm = UsuarioViewModel(service=service)

    # Guardamos el usuario en Firebase para prueba
    ruta = f"{usuario_vm.ruta_usuarios}/{usuario_prueba.correo.replace('@','_at_').replace('.','_dot_')}"
    service.guardar_datos(ruta, usuario_prueba.to_dict())
    print("Usuario guardado en Firebase.")

    # Obtenemos el usuario usando el ViewModel
    usuario_obtenido = usuario_vm.obtener_usuario(usuario_prueba.correo)
    print("Usuario obtenido desde ViewModel:", usuario_obtenido)

# --- Prueba de Grupo ---
def test_grupo_vm():
    print("\n=== Test GruposViewModel ===")
    
    # Creamos un grupo de prueba
    grupo_vm = GruposViewModel(service=service)
    grupo_prueba = grupo_vm.crear_grupo(
        nombre="Grupo Test",
        descripcion="Grupo de prueba",
        categoria="Academico",
        organizadores=["thomas@test.com"]
    )
    print("Grupo creado:", grupo_prueba)

    # Listamos todos los grupos
    grupos = grupo_vm.listar_grupos()
    print("Grupos listados desde ViewModel:", grupos)

    # Agregamos un integrante
    agregado = grupo_vm.agregar_integrante(grupo_prueba['id_grupo'], "usuario2@test.com")
    print("Agregado un integrante:", agregado)

    # Obtenemos el grupo actualizado
    grupo_actualizado = grupo_vm.obtener_grupo(grupo_prueba['id_grupo'])
    print("Grupo actualizado:", grupo_actualizado.to_dict())

# --- Ejecutar tests ---
if __name__ == "__main__":
    test_usuario_vm()
    test_grupo_vm()
