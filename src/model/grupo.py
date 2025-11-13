class Grupo:
    # Clase que representa un grupo estudiantil con varios organizadores.

    def __init__(self, nombre, descripcion, categoria, organizadores, integrantes=None, id_grupo=None, eventos=None):
        # ID único basado en nombre
        self.id_grupo = id_grupo if id_grupo else nombre.replace(" ", "_").lower()
        self.nombre = nombre
        self.descripcion = descripcion
        self.categoria = categoria
        # Revisa si los organizadores son varios y lo trata como lista
        self.organizadores = organizadores if isinstance(organizadores, list) else [organizadores]
        # inicia con todos los organizadores como miembros
        self.integrantes = integrantes if integrantes else self.organizadores.copy()
        # eventos: lista de diccionarios (cada uno representa un evento)
        self.eventos = eventos if eventos else []

    def to_dict(self):
        # Convierte el objeto en un diccionario para Firebase.
        return {
            "id_grupo": self.id_grupo,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "categoria": self.categoria,
            "organizadores": self.organizadores,
            "integrantes": self.integrantes,
            "eventos": self.eventos,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            nombre=d.get("nombre"),
            descripcion=d.get("descripcion"),
            categoria=d.get("categoria"),
            organizadores=d.get("organizadores", []),
            integrantes=d.get("integrantes", []),
            id_grupo=d.get("id_grupo"),
            eventos=d.get("eventos", []),
        )


    def agregar_integrante(self, usuario):
        # Agrega un usuario a la lista de integrantes si no está presente.
        if usuario not in self.integrantes:
            self.integrantes.append(usuario)
            return True
        return False

    def remover_integrante(self, usuario):
        # Elimina un usuario de la lista de integrantes si existe.
        if usuario in self.integrantes:
            self.integrantes.remove(usuario)
            return True
        return False

    def actualizar_info(self, nombre=None, descripcion=None, categoria=None):
        # Actualiza información básica del grupo.
        if nombre:
            self.nombre = nombre
        if descripcion:
            self.descripcion = descripcion
        if categoria:
            self.categoria = categoria

    def tiene_integrante(self, usuario):
        # Verifica si un usuario pertenece al grupo.
        return usuario in self.integrantes

    def es_organizador(self, usuario):
        # Verifica si un usuario es uno de los organizadores.
        return usuario in self.organizadores

    def agregar_organizador(self, usuario):
        # Agrega un organizador al grupo si no está presente.
        if usuario not in self.organizadores:
            self.organizadores.append(usuario)
            # Asegurar que también sea miembro
            if usuario not in self.integrantes:
                self.integrantes.append(usuario)
            return True
        return False

    def remover_organizador(self, usuario):
        # Elimina un organizador del grupo si existe.
        if usuario in self.organizadores:
            self.organizadores.remove(usuario)
            return True
        return False

    def agregar_evento(self, evento_dict):
        """Agrega un evento al grupo (evento_dict debe ser serializable)."""
        if not isinstance(self.eventos, list):
            self.eventos = []
        self.eventos.append(evento_dict)

    def eliminar_evento_por_id(self, id_evento):
        if not self.eventos:
            return False
        before = len(self.eventos)
        self.eventos = [e for e in self.eventos if e.get("id") != id_evento]
        return len(self.eventos) < before