from django.db import models
from .settings import FIRESTORE_DB


class UsuarioTuneFace:
    def __init__(self, nombre, local, imagenes=None, canciones=None):
        self.nombre = nombre
        self.local = local
        self.imagenes = imagenes
        self.canciones = canciones

    def to_dict(self):
        return {
            "nombre": self.nombre,
            "local": self.local,
            "imagenes": self.imagenes,
            "canciones": self.canciones,
        }

    @staticmethod
    def from_dict(data):
        return UsuarioTuneFace(
            nombre=data.get("nombre"),
            local=data.get("local"),
            imagenes=data.get("imagenes"),
            canciones=data.get("canciones"),
        )

    def __str__(self):
        return self.nombre