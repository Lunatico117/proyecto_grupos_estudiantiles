# python -m test.test_auth_vm
# test_auth_vm_real.py
# Este test va a usar Firebase real y creará datos de prueba en tu BD.
# Luego podrás eliminarlos manualmente si quieres.

from src.viewmodel.auth_viewmodel import UsuarioAuthViewModel

def test_auth_viewmodel_real():
    """
    Función de prueba para UsuarioAuthViewModel usando Firebase real.
    Crea un usuario de prueba y verifica el inicio de sesión.
    """

    # Creamos la instancia del ViewModel con el servicio real
    auth_vm = UsuarioAuthViewModel()

    # --- Test de registro ---
    print("Probando registro de usuario...")

    # Datos de prueba
    nombre = "Thomas Test"
    correo = "thomas.test@unal.edu.co"
    password = "123456"
    carrera = "Ingeniería"

    # Registramos el usuario
    resultado_registro = auth_vm.registrar_usuario(
        nombre=nombre,
        correo=correo,
        password=password,
        carrera=carrera
    )

    print("Resultado del registro:", resultado_registro)

    # --- Test de inicio de sesión ---
    print("\nProbando inicio de sesión...")

    resultado_login = auth_vm.iniciar_sesion(
        correo=correo,
        password=password
    )

    print("Resultado del inicio de sesión:", resultado_login)

    # NOTA: Esto dejará el usuario creado en Firebase.
    # Si quieres limpiar después, puedes usar tu UsuarioViewModel o FirebaseService
    # para eliminarlo manualmente.

if __name__ == "__main__":
    test_auth_viewmodel_real()
