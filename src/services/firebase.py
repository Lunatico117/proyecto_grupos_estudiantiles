import firebase_admin
from firebase_admin import credentials, db
import os
from dotenv import load_dotenv

load_dotenv()  # Carga las variables de entorno desde .env

# Obtener las rutas desde las variables de entorno
FIREBASE_CRED_PATH = os.getenv('FIREBASE_CRED_PATH')
FIREBASE_DB_URL = os.getenv('FIREBASE_DB_URL')

if not FIREBASE_CRED_PATH or not FIREBASE_DB_URL:
    raise ValueError("Faltan variables de entorno FIREBASE_CRED_PATH o FIREBASE_DB_URL")

# Inicializar Firebase solo una vez
if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_CRED_PATH)
    firebase_admin.initialize_app(cred, {'databaseURL': FIREBASE_DB_URL})


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
