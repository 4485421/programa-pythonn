from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
import re

from excepciones import ValidacionEntidadError


class EntidadBase(ABC):
    """Clase abstracta que representa entidades generales de Software FJ."""

    def __init__(self, id_entidad: str) -> None:
        if not isinstance(id_entidad, str) or not id_entidad.strip():
            raise ValidacionEntidadError(
                "El identificador de la entidad debe ser un texto no vacío.",
                detalles={"id_entidad": id_entidad},
            )
        self._id_entidad: str = id_entidad.strip().upper()
        self._fecha_creacion: datetime = datetime.now()

    @property
    def id_entidad(self) -> str:
        return self._id_entidad

    @property
    def fecha_creacion(self) -> datetime:
        return self._fecha_creacion

    @abstractmethod
    def resumen(self) -> str:
        """Retorna un resumen legible de la entidad."""


class Cliente(EntidadBase):
    """Representa un cliente de Software FJ con datos personales encapsulados."""

    _EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
    _DOC_REGEX = re.compile(r"^[A-Za-z0-9-]{5,20}$")

    def __init__(
        self,
        id_entidad: str,
        nombre: str,
        documento: str,
        correo: str,
        activo: bool = True,
    ) -> None:
        super().__init__(id_entidad)
        self.nombre = nombre
        self.documento = documento
        self.correo = correo
        self.activo = activo

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not isinstance(valor, str) or len(valor.strip()) < 3:
            raise ValidacionEntidadError(
                "El nombre del cliente debe tener al menos 3 caracteres.",
                detalles={"cliente_id": self._id_entidad, "nombre": valor},
            )
        self._nombre = valor.strip()

    @property
    def documento(self) -> str:
        return self._documento

    @documento.setter
    def documento(self, valor: str) -> None:
        if not isinstance(valor, str) or not self._DOC_REGEX.match(valor.strip()):
            raise ValidacionEntidadError(
                "El documento del cliente es inválido (5 a 20 caracteres alfanuméricos).",
                detalles={"cliente_id": self._id_entidad, "documento": valor},
            )
        self._documento = valor.strip().upper()

    @property
    def correo(self) -> str:
        return self._correo

    @correo.setter
    def correo(self, valor: str) -> None:
        if not isinstance(valor, str) or not self._EMAIL_REGEX.match(valor.strip()):
            raise ValidacionEntidadError(
                "El correo electrónico del cliente no es válido.",
                detalles={"cliente_id": self._id_entidad, "correo": valor},
            )
        self._correo = valor.strip().lower()

    @property
    def activo(self) -> bool:
        return self._activo

    @activo.setter
    def activo(self, valor: bool) -> None:
        if not isinstance(valor, bool):
            raise ValidacionEntidadError(
                "El estado 'activo' debe ser booleano.",
                detalles={"cliente_id": self._id_entidad, "activo": valor},
            )
        self._activo = valor

    def resumen(self) -> str:
        estado = "ACTIVO" if self._activo else "INACTIVO"
        return (
            f"[Cliente {self._id_entidad}] {self._nombre} | "
            f"Doc: {self._documento} | {self._correo} | {estado}"
        )