import xml.etree.ElementTree as ET
import random
import subprocess
import os

def generate_detector_file(taz_file: str, output_file: str):
    """
    Genera un archivo de detectores a partir de un archivo TAZ.
    """
    # Parsear archivo TAZ
    tree = ET.parse(taz_file)
    root = tree.getroot()
    
    # Crear estructura XML para detectores
    detectors = ET.Element('additional')
    
    # Generar detectores para cada edge en cada TAZ
    detector_count = 0
    for taz in root.findall('taz'):
        edges = taz.get('edges').split()
        for edge in edges:
            detector = ET.SubElement(detectors, 'detectorDefinition')
            detector.set('id', f'det_{detector_count}')
            detector.set('lane', f'{edge}_0')  # Asume el primer carril
            detector.set('pos', '0')
            detector.set('freq', '900')
            detector.set('file', './assets/detector_output.xml')
            detector.set('friendlyPos', 'true')
            
            # Valor aleatorio de flujo vehicular (veh/hora)
            detector.set('flow', str(random.randint(50, 300)))
            detector_count += 1

    # Guardar archivo
    ET.ElementTree(detectors).write(output_file, encoding='UTF-8', xml_declaration=True)

def generate_dfrouter_config(net_file: str, detector_file: str, output_base: str):
    """
    Genera un archivo de configuración para dfrouter.
    """
    config = f"""<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <input>
        <net-file value="{net_file}"/>
        <detector-files value="{detector_file}"/>
    </input>
    
    <output>
        <routes-output value="{output_base}.rou.xml"/>
        <emitters-output value="{output_base}.emitters.xml"/>
    </output>
    
    <processing>
        <guess-empty-flows value="true"/>
        <time-step value="60"/>
    </processing>
</configuration>"""
    
    with open('./assets/dfrouter_config.xml', 'w') as f:
        f.write(config)

def generate_trips_and_routes(taz_file: str, net_file: str, output_base: str):
    """
    Genera archivos de viajes y rutas a partir de una matriz OD aleatoria.
    """
    # Generar matriz OD aleatoria
    od_matrix = {}
    tree = ET.parse(taz_file)
    tazs = [taz.get('id') for taz in tree.findall('taz')]
    
    for origin in tazs:
        od_matrix[origin] = {}
        for dest in tazs:
            if origin != dest:
                od_matrix[origin][dest] = random.randint(0, 50)  # Vehículos/hora

    # Generar viajes con od2trips
    subprocess.run([
        'od2trips',
        '-n', net_file,
        '--taz-files', taz_file,
        '--od-matrix', str(od_matrix),
        '-o', f'{output_base}.trips.xml'
    ], check=True)


    # Generar rutas con duarouter
    subprocess.run([
        'duarouter',
        '-n', net_file,
        '-r', f'{output_base}.trips.xml',
        '-o', f'{output_base}.rou.xml',
        '--ignore-errors',
        '--routing-threads', '4'
    ], check=True)


if __name__ == "__main__":
    # Crear carpeta ./assets si no existe
    os.makedirs('./assets', exist_ok=True)

    # Generar archivo de detectores
    generate_detector_file('./assets/hf.taz.xml', './assets/detectors.add.xml')

    # Generar configuración de dfrouter
    generate_dfrouter_config(
        net_file='./assets/red_hidalgo-federalismo.net.xml',
        detector_file='./assets/detectors.add.xml',
        output_base='./assets/traffic-hf'
    )

    # Generar viajes y rutas
    generate_trips_and_routes(
        taz_file='./assets/hf.taz.xml',
        net_file='./assets/red_hidalgo-federalismo.net.xml',
        output_base='./assets/simulation'
    )