import uuid

class Usuario:
    
    # Clase que representa a un usuario dentro del sistema UNAL.
    # Contiene datos personales y algunos métodos de interacción.
    
    def __init__(self, id_usuario, nombre_completo, correo, contraseña, carrera, grupos=None, descripcion_personal=""):
        self.id_usuario = id_usuario              # ID único
        self.nombre_completo = nombre_completo
        self.correo = correo
        self.contraseña = contraseña
        self.carrera = carrera
        self.grupos = grupos if grupos is not None else []  # lista con los IDs de los grupos
        self.descripcion_personal = descripcion_personal  # NUEVO CAMPO

    @classmethod
    def crear_usuario(cls, nombre_completo, correo, contraseña, carrera, descripcion_personal=""):
        if not correo.endswith("@unal.edu.co"):
            raise ValueError("El correo debe ser institucional de la UNAL.")
        id_generado = str(uuid.uuid4())
        return cls(id_generado, nombre_completo, correo, contraseña, carrera, descripcion_personal=descripcion_personal)


    def actualizar_datos(self, **kwargs):
        
        # Actualiza datos del usuario. Ejemplo:
        # usuario.actualizar_datos(nombre_completo="Nuevo Nombre", carrera="Ingeniería Civil")

        for clave, valor in kwargs.items():
            # El hasattr verifica si existe ese atributo en el objeto 
            if hasattr(self, clave):
                # El setattr asigna el valor a la clave 
                setattr(self, clave, valor)
            else:
                print(f"Atributo '{clave}' no existe en Usuario.")


    def unirse_a_grupo(self, id_grupo, servicio=None):

        if id_grupo not in self.grupos:
            self.grupos.append(id_grupo)
            if servicio:
                servicio.agregar_usuario_a_grupo(self.id_usuario, id_grupo)
        else:
            print("El usuario ya pertenece a este grupo.")


    def salirse_de_grupo(self, id_grupo, servicio=None):

        if id_grupo in self.grupos:
            self.grupos.remove(id_grupo)
            if servicio:
                servicio.remover_usuario_de_grupo(self.id_usuario, id_grupo)
        else:
            print("El usuario no pertenece a este grupo.")


    def to_dict(self):

        return {
            "id_usuario": self.id_usuario,
            "nombre_completo": self.nombre_completo,
            "correo": self.correo,
            "contraseña": self.contraseña,
            "carrera": self.carrera,
            "grupos": self.grupos,
            "descripcion_personal": getattr(self, "descripcion_personal", "")
 
        }
    

    def __str__(self):   
        # Representación legible del usuario.

        return f"{self.nombre_completo} ({self.correo}) - {self.carrera}"
