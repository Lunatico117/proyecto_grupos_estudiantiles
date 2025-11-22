import firebase_admin
from firebase_admin import credentials, db
import os
import json
from dotenv import load_dotenv

load_dotenv()  # Carga variables locales si estás en desarrollo

# Variables de entorno necesarias
FIREBASE_CREDENTIALS = os.getenv('FIREBASE_CREDENTIALS')
FIREBASE_DB_URL = os.getenv('FIREBASE_DB_URL')

if not FIREBASE_CREDENTIALS:
    raise ValueError("Falta la variable de entorno FIREBASE_CREDENTIALS")

if not FIREBASE_DB_URL:
    raise ValueError("Falta la variable de entorno FIREBASE_DB_URL")

# Inicializar Firebase solo una vez
if not firebase_admin._apps:
    # Convertir el JSON almacenado en la variable de entorno en un dict
    cred_dict = json.loads(FIREBASE_CREDENTIALS)

    # Crear credenciales desde el dict (sin archivo físico)
    cred = credentials.Certificate(cred_dict)

    # Inicializar Firebase
    firebase_admin.initialize_app(cred, {
        'databaseURL': FIREBASE_DB_URL
    })



class FirebaseService:
    """Servicio para interactuar con Firebase Realtime Database."""

    def obtener_datos(self, ruta):
        ref = db.reference(ruta)
        return ref.get()

    def guardar_datos(self, ruta, datos):
        ref = db.reference(ruta)
        ref.set(datos)

    def eliminar_datos(self, ruta):
        ref = db.reference(ruta)
        ref.delete()

    def actualizar_datos(self, ruta, nuevos_datos):
        ref = db.reference(ruta)
        ref.set(nuevos_datos)

    # Con este solo se actualiza el dato que se le pase
    def actualizar_campo(self, ruta, campo, nuevo_valor):
        datos_actuales = self.obtener_datos(ruta) or {}
        datos_actuales[campo] = nuevo_valor
        self.actualizar_datos(ruta, datos_actuales)

