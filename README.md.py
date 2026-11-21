# Sistema Integral de Gestión - Software FJ

Aplicación orientada a objetos en Python (sin bases de datos) para gestionar clientes, servicios (reservas de salas, alquiler de equipos y asesorías especializadas) y reservas para **Software FJ**, con encapsulación, polimorfismo, sobrecarga de métodos, manejo avanzado de excepciones y registro de eventos en `software_fj.log`.

## Estructura del Proyecto

- `excepciones.py`: Jerarquía de excepciones personalizadas del dominio.
- `entidades.py`: Clase abstracta `EntidadBase` y `Cliente` con encapsulación y validaciones.
- `servicios.py`: Clase abstracta `Servicio`, sobrecarga de cálculo de costos y subclases especializadas (`ReservaSala`, `AlquilerEquipo`, `AsesoriaEspecializada`).
- `reservas.py`: Clase `Reserva` con estados, confirmación, cancelación y procesamiento.
- `gestor.py`: Listas internas en memoria y configuración de logs (`software_fj.log`).
- `main.py`: Simulación de 12 operaciones completas (válidas e inválidas).

## Ejecución

```bash
python main.py