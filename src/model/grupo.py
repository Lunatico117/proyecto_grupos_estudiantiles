class Grupo:
    # Clase que representa un grupo estudiantil con varios organizadores.

    def __init__(self, nombre, descripcion, categoria, organizadores, integrantes=None, id_grupo=None):
        # ID único basado en nombre
        self.id_grupo = id_grupo if id_grupo else nombre.replace(" ", "_").lower()  
        self.nombre = nombre
        self.descripcion = descripcion
        self.categoria = categoria
        # Revisa si los organizadores son varios y lo trata como lista, si es solo uno es el primer elemento de la lista
        self.organizadores = organizadores if isinstance(organizadores, list) else [organizadores]
        # inicia con todos los organizadores como miembros
        self.integrantes = integrantes if integrantes else self.organizadores.copy()  

    def to_dict(self):
        # Convierte el objeto en un diccionario para Firebase.
        return {
            "id_grupo": self.id_grupo,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "categoria": self.categoria,
            "organizadores": self.organizadores,
            "integrantes": self.integrantes
        }

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
