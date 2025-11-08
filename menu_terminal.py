
from src.viewmodel.auth_viewmodel import UsuarioAuthViewModel
from src.services.firebase_global import firebase_global
from src.viewmodel.grupos_viewmodel import GruposViewModel

def mostrar_menu():
    """Muestra el menú principal en consola"""
    print("\n=== MENÚ PRINCIPAL ===")
    print("1. Registrar usuario")
    print("2. Iniciar sesión")
    print("3. Validar datos de usuario")
    print("4. Actualizar datos de usuario")
    print("5. Eliminar usuario")
    print("6. Crear grupo")
    print("7. Eliminar grupo")
    print("8. Actualizar grupo")
    print("0. Salir")


def registrar_usuario(auth_vm):
    """Permite registrar un nuevo usuario en Firebase."""
    print("\n--- REGISTRAR USUARIO ---")
    nombre = input("Nombre completo: ")
    correo = input("Correo institucional: ")
    password = input("Contraseña: ")
    carrera = input("Carrera: ")

    resultado = auth_vm.registrar_usuario(nombre, correo, password, carrera)
    print("\nResultado:", resultado)


def iniciar_sesion(auth_vm):
    """Permite iniciar sesión con un usuario existente."""
    print("\n--- INICIAR SESIÓN ---")
    correo = input("Correo: ")
    password = input("Contraseña: ")

    resultado = auth_vm.iniciar_sesion(correo, password)
    print("\nResultado:", resultado)


def validar_datos(auth_vm):
    """Verifica si los datos ingresados cumplen las validaciones."""
    print("\n--- VALIDAR DATOS ---")
    nombre = input("Nombre: ")
    correo = input("Correo: ")
    password = input("Contraseña: ")
    carrera = input("Carrera: ")

    resultado = auth_vm.validar_datos(nombre, correo, password, carrera)
    print("\nResultado:", resultado)


def actualizar_usuario(firebase_global):
    """Simula la actualización de datos de un usuario existente."""
    print("\n--- ACTUALIZAR USUARIO ---")
    correo = input("Correo del usuario a actualizar: ")
    nuevo_nombre = input("Nuevo nombre: ")

    correo_key = correo.replace('@', '_at_').replace('.', '_dot_')
    ruta = f"usuarios/{correo_key}"

    datos = firebase_global.obtener_datos(ruta)
    if not datos:
        print("Usuario no encontrado.")
        return

    datos["nombre"] = nuevo_nombre
    firebase_global.guardar_datos(ruta, datos)
    print("Usuario actualizado correctamente.")


def eliminar_usuario(firebase_global):
    """Elimina un usuario de Firebase."""
    print("\n--- ELIMINAR USUARIO ---")
    correo = input("Correo del usuario a eliminar: ")

    correo_key = correo.replace('@', '_at_').replace('.', '_dot_')
    ruta = f"usuarios/{correo_key}"

    firebase_global.eliminar_datos(ruta)
    print("Usuario eliminado correctamente.")


def crear_grupo(firebase_global):
    """Simula la creación de un grupo."""
    print("\n--- CREAR GRUPO ---")
    nombre_grupo = input("Nombre del grupo: ")
    descripcion = input("Descripción: ")

    ruta = f"grupos/{nombre_grupo.lower().replace(' ', '_')}"
    data = {"nombre": nombre_grupo, "descripcion": descripcion, "miembros": []}

    firebase_global.guardar_datos(ruta, data)
    print("Grupo creado correctamente.")


def eliminar_grupo(firebase_global):
    """Simula la eliminación de un grupo."""
    print("\n--- ELIMINAR GRUPO ---")
    nombre_grupo = input("Nombre del grupo a eliminar: ")

    ruta = f"grupos/{nombre_grupo.lower().replace(' ', '_')}"
    firebase_global.eliminar_datos(ruta)
    print("Grupo eliminado correctamente.")

def actualizar_grupo(grupos_vm):
    """
    Función que permite actualizar un grupo desde el menú de terminal.
    Recibe la instancia de GruposViewModel con su servicio de Firebase.
    """

    print("\n--- ACTUALIZAR GRUPO ---")
    id_grupo = input("ID del grupo a actualizar: ")
    print("Deja vacío el campo si no deseas modificarlo.")
    nombre = input("Nuevo nombre: ")
    descripcion = input("Nueva descripción: ")
    categoria = input("Nueva categoría: ")

    
    resultado = grupos_vm.actualizar_grupo(
        id_grupo=id_grupo,
        nombre=nombre if nombre else None,
        descripcion=descripcion if descripcion else None,
        categoria=categoria if categoria else None
    )


    print("Grupo actualizado")



def menu():
    """Función principal del programa"""
    auth_vm = UsuarioAuthViewModel(firebase_global)
    grupos_vm = GruposViewModel(firebase_global)

    while True:
        mostrar_menu()
        opcion = input("\nSelecciona una opción: ")

        if opcion == "1":
            registrar_usuario(auth_vm)
        elif opcion == "2":
            iniciar_sesion(auth_vm)
        elif opcion == "3":
            validar_datos(auth_vm)
        elif opcion == "4":
            actualizar_usuario(firebase_global )
        elif opcion == "5":
            eliminar_usuario(firebase_global)
        elif opcion == "6":
            crear_grupo(firebase_global)
        elif opcion == "7":
            eliminar_grupo(firebase_global)
        elif opcion == "8":
            actualizar_grupo(grupos_vm)
        elif opcion == "0":
            print("Saliendo del programa...")
            break
        else:
            print("Opción inválida, intenta de nuevo.")


if __name__ == "__main__":
    menu()
