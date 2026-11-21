from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional


class ErrorSoftwareFJ(Exception):
    """Excepción base del dominio de Software FJ."""

    def __init__(
        self,
        mensaje: str,
        codigo: str = "SFJ-000",
        detalles: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.codigo = codigo
        self.detalles = detalles or {}
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "codigo": self.codigo,
            "mensaje": self.mensaje,
            "detalles": self.detalles,
            "timestamp": self.timestamp,
        }


class ValidacionEntidadError(ErrorSoftwareFJ):
    """Error por datos inválidos o parámetros faltantes."""

    def __init__(self, mensaje: str, detalles: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(mensaje, codigo="SFJ-101", detalles=detalles)


class ServicioNoDisponibleError(ErrorSoftwareFJ):
    """Error cuando el servicio no está disponible o no tiene cupo."""

    def __init__(self, mensaje: str, detalles: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(mensaje, codigo="SFJ-202", detalles=detalles)


class OperacionReservaError(ErrorSoftwareFJ):
    """Error por operaciones o estados inválidos en reservas."""

    def __init__(self, mensaje: str, detalles: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(mensaje, codigo="SFJ-303", detalles=detalles)


class CalculoInconsistenteError(ErrorSoftwareFJ):
    """Error ante cálculos de tarifas, descuentos, impuestos o duraciones inválidos."""

    def __init__(self, mensaje: str, detalles: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(mensaje, codigo="SFJ-404", detalles=detalles)