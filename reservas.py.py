from __future__ import annotations

from enum import Enum
import logging
from typing import Optional

from entidades import Cliente, EntidadBase
from excepciones import (
    ErrorSoftwareFJ,
    OperacionReservaError,
    ServicioNoDisponibleError,
    ValidacionEntidadError,
)
from servicios import Servicio

logger = logging.getLogger("SoftwareFJLogger")


class EstadoReserva(str, Enum):
    PENDIENTE = "PENDIENTE"
    CONFIRMADA = "CONFIRMADA"
    CANCELADA = "CANCELADA"
    FALLIDA = "FALLIDA"


class Reserva(EntidadBase):
    """Integra Cliente, Servicio, duración y estado con control de ciclo de vida."""

    def __init__(
        self,
        id_entidad: str,
        cliente: Cliente,
        servicio: Servicio,
        duracion: float,
        descuento_pct: float = 0.0,
        impuesto: float = 0.19,
    ) -> None:
        super().__init__(id_entidad)
        if not isinstance(cliente, Cliente):
            raise ValidacionEntidadError("Se requiere una instancia válida de Cliente.")
        if not isinstance(servicio, Servicio):
            raise ValidacionEntidadError("Se requiere una instancia válida de Servicio.")
        if not isinstance(duracion, (int, float)) or isinstance(duracion, bool) or duracion <= 0:
            raise ValidacionEntidadError(
                "La duración de la reserva debe ser mayor que cero.",
                detalles={"duracion": duracion},
            )

        self.cliente: Cliente = cliente
        self.servicio: Servicio = servicio
        self.duracion: float = float(duracion)
        self.descuento_pct: float = float(descuento_pct)
        self.impuesto: float = float(impuesto)
        self.estado: EstadoReserva = EstadoReserva.PENDIENTE
        self.monto_total: Optional[float] = None

    def procesar(self) -> float:
        """Valida disponibilidad, calcula el costo y prepara la reserva."""
        try:
            if not self.cliente.activo:
                raise OperacionReservaError(
                    f"El cliente '{self.cliente.nombre}' está inactivo.",
                    detalles={"cliente_id": self.cliente.id_entidad, "reserva_id": self._id_entidad},
                )
            if not self.servicio.disponible:
                raise ServicioNoDisponibleError(
                    f"El servicio '{self.servicio.nombre}' no está disponible.",
                    detalles={"servicio_id": self.servicio.id_entidad, "reserva_id": self._id_entidad},
                )
            if self.estado == EstadoReserva.CANCELADA:
                raise OperacionReservaError(
                    "No se puede procesar una reserva cancelada.",
                    detalles={"reserva_id": self._id_entidad},
                )

            total = self.servicio.calcular_costo_ajustado(
                {"duracion": self.duracion, "descuento_pct": self.descuento_pct},
                impuesto=self.impuesto,
            )
            self.monto_total = total
            return total
        except ErrorSoftwareFJ as err:
            self.estado = EstadoReserva.FALLIDA
            logger.error(f"Error al procesar reserva {self._id_entidad}: {err.to_dict()}")
            raise
        except Exception as exc:
            self.estado = EstadoReserva.FALLIDA
            wrapped = OperacionReservaError(
                f"Fallo inesperado al procesar la reserva {self._id_entidad}.",
                detalles={"reserva_id": self._id_entidad},
            )
            logger.exception(f"Excepción encadenada en reserva {self._id_entidad}")
            raise wrapped from exc

    def confirmar(self) -> str:
        """Confirma una reserva válida."""
        if self.estado == EstadoReserva.CANCELADA:
            raise OperacionReservaError(
                f"La reserva {self._id_entidad} está cancelada y no puede confirmarse.",
                detalles={"reserva_id": self._id_entidad},
            )
        if self.monto_total is None:
            self.procesar()

        self.estado = EstadoReserva.CONFIRMADA
        logger.info(
            f"Reserva {self._id_entidad} CONFIRMADA para {self.cliente.nombre} "
            f"por ${self.monto_total:,.2f}."
        )
        return f"Reserva {self._id_entidad} confirmada por ${self.monto_total:,.2f}."

    def cancelar(self, motivo: str = "Cancelación solicitada") -> str:
        """Cancela una reserva activa o pendiente."""
        if self.estado == EstadoReserva.CANCELADA:
            raise OperacionReservaError(
                f"La reserva {self._id_entidad} ya se encuentra cancelada.",
                detalles={"reserva_id": self._id_entidad},
            )
        if not isinstance(motivo, str) or not motivo.strip():
            raise ValidacionEntidadError(
                "Debe indicar un motivo válido de cancelación.",
                detalles={"reserva_id": self._id_entidad},
            )

        self.estado = EstadoReserva.CANCELADA
        logger.warning(f"Reserva {self._id_entidad} CANCELADA. Motivo: {motivo.strip()}")
        return f"Reserva {self._id_entidad} cancelada ({motivo.strip()})."

    def resumen(self) -> str:
        monto_str = f"${self.monto_total:,.2f}" if self.monto_total is not None else "Sin calcular"
        return (
            f"[Reserva {self._id_entidad}] {self.estado.value} | "
            f"Cliente: {self.cliente.nombre} | Servicio: {self.servicio.nombre} | "
            f"Duración: {self.duracion} | Total: {monto_str}"
        )