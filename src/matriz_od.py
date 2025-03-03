import random
import os
import subprocess
from collections import defaultdict

# Nodos de entrada y salida con conteos de vehículos
conteo_entrada = {
    6511798196: 100, 1369105748: 150, 1460325835: 200,
    801436652: 120, 962426129: 80, 7768286947: 90,
    291180165: 110, 1767721271: 130
}

conteo_salida = {
    7914822015: 90, 1369105724: 140, 1369105748: 160,
    1374261327: 100, 1460325415: 110, 7768286942: 85,
    1369529285: 95, 1339256780: 120, 801504802: 105,
    1341839824: 115
}

# Configuración
OUTPUT_MATRIX = "./assets/od_matrix.txt"
OUTPUT_TAZ = "./assets/taz.xml"
OUTPUT_TRIPS = "./assets/od.traffic.trips.xml"
OD2TRIPS = "od2trips"

if __name__ == "__main__":
    # Crear directorio si no existe
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(os.path.join(script_dir, "assets"), exist_ok=True)
    os.chdir(script_dir)

    # Generar pares OD válidos (origen != destino)
    od_pairs = []
    for origen in conteo_entrada:
        for destino in conteo_salida:
            if origen != destino:
                od_pairs.append((origen, destino))

    # Generar matriz de demanda basada en los conteos
    matrix = defaultdict(int)
    for origen, total_entrada in conteo_entrada.items():
        destinos_disponibles = [destino for destino in conteo_salida if destino != origen]
        for _ in range(total_entrada):
            destino = random.choice(destinos_disponibles)
            matrix[(origen, destino)] += 1

    # Guardar la matriz en formato TXT (sin encabezado)
    with open(OUTPUT_MATRIX, "w") as f:
        for (origen, destino), count in matrix.items():
            f.write(f"{origen} {destino} {count}\n")

    print(f"Matriz OD generada: {OUTPUT_MATRIX}")

    # Crear archivo TAZ
    edges = list(conteo_entrada.keys()) + list(conteo_salida.keys())
    with open(OUTPUT_TAZ, "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<additional>\n')
        for edge in edges:
            f.write(f'    <taz id="{edge}" edges="{edge}"/>\n')
        f.write('</additional>\n')

    print(f"Archivo TAZ generado: {OUTPUT_TAZ}")

    # Ejecutar od2trips
    print("Generando archivo de rutas con od2trips...")
    subprocess.run([
        OD2TRIPS,
        "--od-matrix-files", OUTPUT_MATRIX,  # Parámetro correcto para la matriz OD
        "--taz-files", OUTPUT_TAZ,          # Archivo TAZ generado
        "--output-file", OUTPUT_TRIPS,      # Archivo de salida
        "--vtype", "passenger",             # Tipo de vehículo
        "--begin", "0",                     # Tiempo de inicio
        "--end", "3600"                     # Tiempo final
    ])

    print(f"Archivo de rutas generado: {OUTPUT_TRIPS}")