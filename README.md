Índice

* [Descripción General](#descripción-general)
* [Estructura del Proyecto](#estructura-del-proyecto)
* [Módulos Principales](#módulos-principales)
* [Parámetros de Simulación](#parámetros-de-simulación)
* [Instalación y Configuración](#instalación-y-configuración)
* [Ejemplos de uso](#ejemplos-de-uso)

## Descripción General

Este proyecto proporciona una plataforma modular para simular y optimizar el control de semáforos en redes de tráfico urbano mediante SUMO y TraCI. Utiliza algoritmos bioinspirados (Random Search, Hill Climbing, Particle Swarm Optimization, Simulated Annealing y Algoritmos Genéticos) para ajustar los tiempos de fase de los semáforos, con el objetivo de mejorar métricas como flujo vehicular, velocidad promedio y tiempo de espera. Los resultados se almacenan en archivos JSON para su posterior análisis y comparación.

## Estructura del Proyecto

```plaintext
.
├── pyproject.toml
├── README.md
├── src/
│   ├── assets/                # Red, rutas y configuración generada
│   ├── data/                  # Resultados de simulación y optimización (.json)
│   ├── data_writer.py         # Manejo de persistencia de resultados
│   ├── lights_functions.py    # Lógica de semáforos y cálculo de métricas
│   ├── main.py                # Funciones de generación, prueba y optimización
│   ├── optimization/          # Implementaciones de algoritmos
│   ├── parameters.py          # Parámetros globales de simulación
│   ├── randomTrips.py         # Generación de viajes
│   ├── sumo_simulation.py     # Wrapper de SUMO/TraCI
│   ├── traffic_demand.py      # Generación de matriz OD y archivos TAZ/OD
│   └── utils.py               # Funciones auxiliares
```

## Módulos Principales

### sumo\_simulation.py

* Generación de redes y rutas (`netconvert`, `duarouter`, `od2trips`).
* Control del ciclo de simulación (`start_simulation`, `run_simulation`, `end_simulation`).
* Extracción de métricas y estados de semáforos.

### traffic\_demand.py

* Lectura de CSV de demandas de tráfico.
* Equilibrado de volúmenes de entrada y salida.
* Generación de matriz OD y archivos TAZ/OD.

### lights\_functions.py

* Obtención de fases actuales de semáforos.
* Función objetivo para evaluar configuraciones.
* Aplicación de nuevos tiempos de fase y cálculo de métricas.

### data\_writer.py

* Almacenamiento iterativo de resultados en JSON.
* Lectura y extracción de la mejor configuración.

### optimization/

Contiene implementaciones de:

* Random Search (`random_simulation`)
* Hill Climbing (`hill_simulation`)
* Particle Swarm Optimization (`swarm_simulation`)
* Simulated Annealing (`tsp_sa`)
* Algoritmos Genéticos (`genetic_simulation`)

Cada función recibe la interfaz de semáforos, los rangos mínimos y máximos de tiempo, y devuelve vectores de fase optimizados.

### main.py

Agrupa funciones de alto nivel:

* `generate_files(net, in_d, out_d, time)`: genera los archivos `.taz`, `.od`, `.trip`, `.rou` y `.sumocfg`.
* `test_simulation(config, steps)`: ejecuta una simulación de prueba y devuelve métricas.
* `optimice_trafficlights(config, cars, data=None)`: aplica Simulated Annealing y guarda resultados.
* `check_data()`: lee resultados previos para cada algoritmo y retorna la mejor configuración.
* `show_cases(config, data)`: reproduce visualmente las configuraciones óptimas.

## Parámetros de Simulación

Los valores predeterminados se definen en `parameters.py`:

| Parámetro                    | Descripción                              |
| ---------------------------- | ---------------------------------------- |
| `STEPS`                      | Número de pasos por simulación           |
| `GREEN_RED_MAX_TIME_SECONDS` | Tiempo máximo fase verde/rojo (segundos) |
| `GEEEN_RED_MIN_TIME_SECONDS` | Tiempo mínimo fase verde/rojo (segundos) |
| `YELLOW_MAX_TIME_SECONDS`    | Tiempo máximo fase amarillo (segundos)   |
| `YELLO_MIN_TIME_SECONDS`     | Tiempo mínimo fase amarillo (segundos)   |
| `START_TIME`, `END_TIME`     | Hora de inicio y fin de la simulación    |

## Instalación y Configuración

1. Instalar SUMO y agregar al `PATH` ([https://sumo.dlr.de/docs/Downloads.php](https://sumo.dlr.de/docs/Downloads.php)).
2. Instalar Python 3.12 o superior.
3. Instalar TraCI:

   ```bash
   pip install traci
   ```

## Ejemplos de uso

A continuación, se presentan ejemplos de cómo se pueden utilizar las funciones y módulos del proyecto

### 1. Generación de archivos de configuración

```python
from src.main import generate_files
from src.traffic_demand import TrafficDemand

in_d = TrafficDemand.read_csv("./assets/entrada.csv")
out_d = TrafficDemand.read_csv("./assets/salida.csv")
time_window = "08:00 09:00"
config = generate_files("./assets/map.net.xml", in_d, out_d, time_window)
```

### 2. Ejecución de simulación de prueba

```python
from src.sumo_simulation import SumoSimulation

sumo = SumoSimulation(config)
sumo.start_simulation(False)
result = sumo.run_simulation(100)
sumo.end_simulation()
print(result)
```

### 3. Optimización con Simulated Annealing

```python
from src.data_writer import DataWriter
from src.lights_functions import LightsFunctions
from src.optimization.simmulated_annealing import tsp_sa

# Preparación
data_writer = DataWriter('sa', 'data')
lf = LightsFunctions(config, cars, steps=100, data_writer=data_writer)
x_low, x_high = lf.get_min_max(10, 60, 3, 6)

# Simulated Annealing
_, _, sa_results = tsp_sa(lf.all_lights, x_low, x_high, max_iter=100)
for entry in sa_results:
    data_writer.add_data(entry)
data_writer.write_file()
```

### 4. Optimización con Random Search

```python
from src.data_writer import DataWriter
from src.lights_functions import LightsFunctions
from src.optimization.random import random_simulation

writer = DataWriter('random', 'data')
lf = LightsFunctions(config, cars, steps=100, data_writer=writer)
x_low, x_high = lf.get_min_max(10, 60, 3, 6)
_, _, random_results = random_simulation(lf.all_lights, x_low, x_high, iterations=50)
for entry in random_results:
    writer.add_data(entry)
writer.write_file()
```

### 5. Optimización con Hill Climbing

```python
from src.data_writer import DataWriter
from src.lights_functions import LightsFunctions
from src.optimization.hill_climbing import hill_simulation

writer = DataWriter('hill', 'data')
lf = LightsFunctions(config, cars, steps=100, data_writer=writer)
x_low, x_high = lf.get_min_max(10, 60, 3, 6)
hill_simulation(lf.all_lights, x_low, x_high, max_iter=100)
```

### 6. Optimización con Particle Swarm Optimization

```python
from src.data_writer import DataWriter
from src.lights_functions import LightsFunctions
from src.optimization.pso import swarm_simulation

writer = DataWriter('swarm', 'data')
lf = LightsFunctions(config, cars, steps=100, data_writer=writer)
x_low, x_high = lf.get_min_max(10, 60, 3, 6)
swarm_simulation(lf.all_lights, x_low, x_high, swarm_size=20, max_iter=100)
```

### 7. Optimización con Algoritmos Genéticos

```python
from src.data_writer import DataWriter
from src.lights_functions import LightsFunctions
from src.optimization.genetic import genetic_simulation

writer = DataWriter('genetic', 'data')
lf = LightsFunctions(config, cars, steps=100, data_writer=writer)
x_low, x_high = lf.get_min_max(10, 60, 3, 6)
_, _, genetic_results = genetic_simulation(
    lf.all_lights, x_low, x_high,
    population_size=100,
    generations=50,
    lower_bound=-5,
    upper_bound=105
)
for entry in genetic_results:
    writer.add_data(entry)
writer.write_file()
```

### 8. Visualización de casos optimizados

```python
from src.lights_functions import LightsFunctions
from src.data_writer import DataWriter

# Leer mejor configuración desde JSON
writer = DataWriter('sa', 'data')
writer.read_file()
best = writer.best

# Visualizar en SUMO
lfs = LightsFunctions(config, cars, steps=200)
lfs.all_lights(best['x'], visual=True)
```