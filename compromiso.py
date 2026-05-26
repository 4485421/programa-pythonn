# Datos de clientes
matriz = [
    [1, 200, 10],
    [2, 50, 2],
    [3, 100, 5],
    [4, 250, 9],
    [5, 40, 1]
]

def clasificar(duracion, clics):
    if duracion > 180 and clics > 8:
        return "Alto"
    elif duracion < 60 or clics < 3:
        return "Bajo"
    else:
        return "Medio"

print("Informe de compromiso")

for cliente in matriz:
    resultado = clasificar(cliente[1], cliente[2])
    print("Cliente", cliente[0], "-", resultado)
