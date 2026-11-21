from __future__ import annotations

import logging
from typing import List

from entidades import Cliente
from excepciones import OperacionReservaError, ValidacionEntidadError
from reservas import Reserva
from servicios import Servicio


def configurar_logger(ruta_log: str = "software_fj.log") -> logging.Logger:
    logger = logging.getLogger("SoftwareFJLogger")
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        formato = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler = logging.FileHandler(ruta_log, mode="a", encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formato)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formato)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger


logger = configurar_logger()


class GestorSoftwareFJ:
    """Gestiona clientes, servicios y reservas en listas en memoria (sin BD)."""

    def __init__(self) -> None:
        self.clientes: List[Cliente] = []
        self.servicios: List[Servicio] = []
        self.reservas: List[Reserva] = []

    def registrar_cliente(self, cliente: Cliente) -> Cliente:
        if any(c.id_entidad == cliente.id_entidad for c in self.clientes):
            raise ValidacionEntidadError(
                f"Ya existe un cliente registrado con ID {cliente.id_entidad}.",
                detalles={"cliente_id": cliente.id_entidad},
            )
        self.clientes.append(cliente)
        logger.info(f"Cliente registrado: {cliente.resumen()}")
        return cliente

    def registrar_servicio(self, servicio: Servicio) -> Servicio:
        if any(s.id_entidad == servicio.id_entidad for s in self.servicios):
            raise ValidacionEntidadError(
                f"Ya existe un servicio registrado con ID {servicio.id_entidad}.",
                detalles={"servicio_id": servicio.id_entidad},
            )
        self.servicios.append(servicio)
        logger.info(f"Servicio registrado: {servicio.resumen()}")
        return servicio

    def crear_y_procesar_reserva(self, reserva: Reserva, confirmar_inmediato: bool = True) -> Reserva:
        if any(r.id_entidad == reserva.id_entidad for r in self.reservas):
            raise OperacionReservaError(
                f"Ya existe una reserva registrada con ID {reserva.id_entidad}.",
                detalles={"reserva_id": reserva.id_entidad},
            )
        self.reservas.append(reserva)
        reserva.procesar()
        if confirmar_inmediato:
            reserva.confirmar()
        return reserva