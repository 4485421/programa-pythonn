from __future__ import annotations

import os
from typing import List, Optional

from entidades import Cliente
from excepciones import ErrorSoftwareFJ
from gestor import GestorSoftwareFJ, logger
from reservas import Reserva
from servicios import AlquilerEquipo, AsesoriaEspecializada, ReservaSala


def ejecutar_simulacion() -> None:
    gestor = GestorSoftwareFJ()
    resultados: List[str] = []

    operaciones = [
        "OP-01: Registro válido de Cliente CLI-01",
        "OP-02: Registro inválido de Cliente (correo sin formato válido)",
        "OP-03: Registro válido de Servicio ReservaSala SER-SALA-1",
        "OP-04: Registro válido de Servicio AlquilerEquipo SER-EQ-1",
        "OP-05: Registro válido de Servicio AsesoriaEspecializada SER-ASE-1",
        "OP-06: Registro inválido de Servicio (falta parámetro obligatorio)",
        "OP-07: Reserva exitosa de Sala para CLI-01 (3 horas)",
        "OP-08: Reserva exitosa de Equipo para CLI-01 (2 días, 10% descuento)",
        "OP-09: Reserva fallida por servicio no disponible (SER-ASE-1)",
        "OP-10: Reserva fallida por duración inválida (-2)",
        "OP-11: Cancelación válida de reserva RES-01",
        "OP-12: Intento inválido de cancelar nuevamente RES-01",
    ]

    cliente_valido: Optional[Cliente] = None
    sala: Optional[ReservaSala] = None
    equipo: Optional[AlquilerEquipo] = None
    asesoria: Optional[AsesoriaEspecializada] = None
    reserva_01: Optional[Reserva] = None

    for op in operaciones:
        estado_op = "OK"
        try:
            if op.startswith("OP-01"):
                cliente_valido = Cliente(
                    id_entidad="cli-01",
                    nombre="Laura Méndez",
                    documento="CC10987654",
                    correo="laura.mendez@empresa.co",
                    activo=True,
                )
                gestor.registrar_cliente(cliente_valido)

            elif op.startswith("OP-02"):
                cliente_invalido = Cliente(
                    id_entidad="cli-02",
                    nombre="Carlos Ruiz",
                    documento="CC11223344",
                    correo="correo_invalido",
                )
                gestor.registrar_cliente(cliente_invalido)

            elif op.startswith("OP-03"):
                sala = ReservaSala(
                    id_entidad="ser-sala-1",
                    nombre="Sala de Juntas Andromeda",
                    tarifa_base=80000.0,
                    disponible=True,
                    parametros={"capacidad_personas": 12, "ubicacion": "Piso 3 - Sede Norte"},
                )
                gestor.registrar_servicio(sala)

            elif op.startswith("OP-04"):
                equipo = AlquilerEquipo(
                    id_entidad="ser-eq-1",
                    nombre="Laptop Workstation i7 32GB",
                    tarifa_base=65000.0,
                    disponible=True,
                    parametros={"tipo_equipo": "Portátil Alto Rendimiento", "unidades_disponibles": 5},
                )
                gestor.registrar_servicio(equipo)

            elif op.startswith("OP-05"):
                asesoria = AsesoriaEspecializada(
                    id_entidad="ser-ase-1",
                    nombre="Consultoría Microservicios y Cloud",
                    tarifa_base=150000.0,
                    disponible=False,
                    parametros={"especialidad": "Arquitectura Cloud", "modalidad": "REMOTA"},
                )
                gestor.registrar_servicio(asesoria)

            elif op.startswith("OP-06"):
                servicio_invalido = ReservaSala(
                    id_entidad="ser-sala-err",
                    nombre="Sala Incompleta",
                    tarifa_base=50000.0,
                    parametros={"capacidad_personas": 6},
                )
                gestor.registrar_servicio(servicio_invalido)

            elif op.startswith("OP-07"):
                assert cliente_valido is not None and sala is not None
                reserva_01 = Reserva(
                    id_entidad="res-01",
                    cliente=cliente_valido,
                    servicio=sala,
                    duracion=3,
                )
                gestor.crear_y_procesar_reserva(reserva_01, confirmar_inmediato=True)

            elif op.startswith("OP-08"):
                assert cliente_valido is not None and equipo is not None
                reserva_02 = Reserva(
                    id_entidad="res-02",
                    cliente=cliente_valido,
                    servicio=equipo,
                    duracion=2,
                    descuento_pct=0.10,
                )
                gestor.crear_y_procesar_reserva(reserva_02, confirmar_inmediato=True)

            elif op.startswith("OP-09"):
                assert cliente_valido is not None and asesoria is not None
                reserva_03 = Reserva(
                    id_entidad="res-03",
                    cliente=cliente_valido,
                    servicio=asesoria,
                    duracion=2,
                )
                gestor.crear_y_procesar_reserva(reserva_03, confirmar_inmediato=True)

            elif op.startswith("OP-10"):
                assert cliente_valido is not None and sala is not None
                reserva_04 = Reserva(
                    id_entidad="res-04",
                    cliente=cliente_valido,
                    servicio=sala,
                    duracion=-2,
                )
                gestor.crear_y_procesar_reserva(reserva_04, confirmar_inmediato=True)

            elif op.startswith("OP-11"):
                assert reserva_01 is not None
                reserva_01.cancelar("Cambio de agenda del cliente")

            elif op.startswith("OP-12"):
                assert reserva_01 is not None
                reserva_01.cancelar("Segundo intento de cancelación")

        except ErrorSoftwareFJ as err:
            estado_op = f"MANEJADA ({err.codigo}): {err.mensaje}"
            logger.error(f"{op} -> {estado_op} | Detalles: {err.detalles}")
        except Exception as exc:
            estado_op = f"NO PREVISTA: {type(exc).__name__}: {exc}"
            logger.exception(f"{op} -> {estado_op}")
        else:
            logger.info(f"{op} -> COMPLETADA EXITOSAMENTE")
        finally:
            resultados.append(f"{op} => {estado_op}")

    print("\n=== RESUMEN DE 12 OPERACIONES SIMULADAS (SOFTWARE FJ) ===")
    for linea in resultados:
        print(" -", linea)

    print(f"\nTotal clientes en memoria: {len(gestor.clientes)}")
    print(f"Total servicios en memoria: {len(gestor.servicios)}")
    print(f"Total reservas en memoria: {len(gestor.reservas)}")
    print(f"Archivo de logs generado en: {os.path.abspath('software_fj.log')}")


if __name__ == "__main__":
    ejecutar_simulacion()