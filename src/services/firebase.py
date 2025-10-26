import firebase_admin
from firebase_admin import credentials, db
import os

# Usar variable de entorno o dejar la ruta configurable
FIREBASE_CRED_PATH = os.getenv('FIREBASE_CRED_PATH', '.env/grupos-estudiantiles-c9f85-firebase-adminsdk-fbsvc-76389fb542.json"')
FIREBASE_DB_URL = os.getenv('FIREBASE_DB_URL', 'https://grupos-estudiantiles-c9f85-default-rtdb.firebaseio.com/')

# Inicializar Firebase solo una vez
if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_CRED_PATH)
    firebase_admin.initialize_app(cred, {
        'databaseURL': FIREBASE_DB_URL
    })

class FirebaseService:
    """Servicio reutilizable para acceso a Firebase Realtime Database."""

    def __init__(self):
        pass
    
    def obtener_datos(self, ruta):
        ref = db.reference(ruta)
        return ref.get()

    def guardar_datos(self, ruta, datos):
        ref = db.reference(ruta)
        ref.set(datos)

    def actualizar_datos(self, ruta, datos):
        ref = db.reference(ruta)
        ref.update(datos)

    def eliminar_datos(self, ruta):
        ref = db.reference(ruta)
        ref.delete()