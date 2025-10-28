# src/utils/validaciones.py
# Funciones de validación comunes para el proyecto.

def es_correo_valido(correo: str) -> bool:
    """
    Verifica que el correo sea institucional de la UNAL.
    Retorna True si termina en '@unal.edu.co', False en caso contrario.
    """
    return isinstance(correo, str) and correo.endswith("@unal.edu.co")
