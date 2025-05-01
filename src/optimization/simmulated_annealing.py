import random
import math
from multiprocessing import Pool
import copy

def swap(solution, i, j):
    solution[i], solution[j] = solution[j], solution[i]
    return solution

def inverse(solution, i, j):
    solution[i:j+1] = list(reversed(solution[i:j+1]))
    return solution

def insert(solution, i, j):
    solution.insert(j, solution.pop(i))
    return solution

def _sa_worker(args):
    func, xl, xh, max_iter, initial_temp, cooling_rate, worker_id = args
    
    # Inicializar con una solución aleatoria
    n = len(xl)
    current_solution = [random.uniform(xl[i], xh[i]) for i in range(n)]
    current_value, current_data = func(current_solution)
    
    # Almacenar la mejor solución
    best_solution = copy.deepcopy(current_solution)
    best_value = current_value
    
    # Datos generados durante la ejecución
    generated_data = [current_data]
    
    # Temperatura actual
    T = initial_temp
    alpha = cooling_rate
    
    # Operaciones de perturbación para valores reales
    perturbations = [
        # Lambda para perturbación tipo swap pero adaptada a valores reales
        lambda sol, i, j: swap(sol[:], i, j),
        
        # Lambda para perturbación local (cambio pequeño en un valor)
        lambda sol, i, j: [
            sol[k] + random.uniform(-0.1, 0.1) * (xh[k] - xl[k]) 
            if k == i or k == j else sol[k] 
            for k in range(len(sol))
        ],
        
        # Lambda para perturbación global (cambio en todos los valores)
        lambda sol, i, j: [
            sol[k] + random.uniform(-0.05, 0.05) * (xh[k] - xl[k])
            for k in range(len(sol))
        ]
    ]
    
    def ensure_bounds(sol):
        return [max(xl[i], min(xh[i], sol[i])) for i in range(n)]
    
    # Proceso principal de recocido simulado
    for _ in range(max_iter):
        # Seleccionar posiciones aleatorias para perturbación
        i, j = sorted([random.randint(0, n-1), random.randint(0, n-1)])
        while i == j and n > 1:
            j = random.randint(0, n-1)
        
        perturbation = perturbations[random.randint(0, len(perturbations)-1)]
        new_solution = ensure_bounds(perturbation(current_solution, i, j))
        
        new_value, new_data = func(new_solution)
        generated_data.append(new_data)
        
        delta = current_value - new_value
        
        if delta > 0 or random.random() < math.exp(delta / T):
            current_solution = new_solution
            current_value = new_value
            
            if current_value < best_value:
                best_solution = copy.deepcopy(current_solution)
                best_value = current_value
        
        T *= alpha
        
        if T < 0.01:
            break
    
    return best_solution, best_value, generated_data

def tsp_sa(func, xl, xh, max_iter=1000, initial_temp=100, cooling_rate=0.99, cores=8, num_runs=8):
    args_list = [
        (func, xl, xh, max_iter, initial_temp, cooling_rate, i) 
        for i in range(num_runs)
    ]
    
    # Ejecutar múltiples instancias en paralelo
    with Pool(processes=min(cores, num_runs)) as pool:
        results = pool.map(_sa_worker, args_list)
    
    best_solution = None
    best_value = float('inf')
    all_data = []
    
    for solution, value, data in results:
        all_data.extend(data)
        
        if value < best_value:
            best_solution = solution
            best_value = value
    
    return best_solution, best_value, all_data
