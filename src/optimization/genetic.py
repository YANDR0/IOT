from random import random, randint
import functools
import copy
from multiprocessing import Pool

class Individual:
    def __init__(self, xl, xh):
        self.N = len(xl)
        self.genotype = [randint(0, 9) for _ in range(6*self.N)]
        self.phenotype = [0 for _ in range(self.N)]
        self.toPhenotype(xl, xh)
        self.fitness = 0
        self.expected_value = 0
        
    def toPhenotype(self, xl, xh):
        max_num = 10**6 - 1
        for i in range(self.N):
            section = self.genotype[i*6: (i+1)*6]
            chromo = functools.reduce(lambda x, y: x * 10 + y, section)
            self.phenotype[i] = xl[i] + chromo/max_num * (xh[i] - xl[i])

def createPop(M, xl, xh):
    return [Individual(xl, xh) for _ in range(M)]

def _evaluate_task(args):
    phenotype, func, fxl, fxh = args
    result = func(phenotype)
    
    # Si el resultado es una tupla (valor, datos), desempaquetamos
    if isinstance(result, tuple) and len(result) == 2:
        y, data = result
    else:
        # Si el resultado es solo un valor, asumimos que no hay datos adicionales
        y = result
        data = None
        
    # Cálculo del fitness
    fitness_val = 1 - (y - fxl) / (fxh - fxl) if (fxh - fxl) != 0 else 0
    return fitness_val, data

def evaluate_fitness_parallel(func, pop, fxl, fxh, cores=8):
    tasks = [(ind.phenotype, func, fxl, fxh) for ind in pop]
    
    with Pool(processes=cores) as pool:
        results = pool.map(_evaluate_task, tasks)
    
    fitnesses = [r[0] for r in results]
    all_data = [r[1] for r in results if r[1] is not None]  # Filtramos los None
    
    return fitnesses, all_data

def update_fitness(func, pop, fxl, fxh, cores=8):
    fitnesses, all_data = evaluate_fitness_parallel(func, pop, fxl, fxh, cores)
    
    # Actualizar fitness para cada individuo
    for ind, fit_val in zip(pop, fitnesses):
        ind.fitness = fit_val
    
    # Encontrar el mejor individuo
    best = copy.deepcopy(max(pop, key=lambda x: x.fitness))
    
    return best, all_data

def selection(pop):
    # Implementación más parecida a la original
    pop_sorted = sorted(pop, key=lambda x: x.fitness)
    N = len(pop_sorted)
    
    # Calcular expected_value para cada individuo
    for i in range(N):
        pop_sorted[i].expected_value = 0.9 + (1.1 - 0.9) * i / (N - 1)
    
    # Agregar el mejor individuo directamente a la nueva población (elitismo)
    new_list = [copy.deepcopy(pop_sorted[-1])]
    
    # Selección por ruleta para el resto
    total_expected = sum(ind.expected_value for ind in pop_sorted)
    
    for _ in range(N-1):
        pick = random() * total_expected
        sum_val = 0
        i = 0
        while sum_val < pick and i < N:
            sum_val += pop_sorted[i].expected_value
            i += 1
        
        if i > 0:  # Asegurarse de que i está dentro de los límites
            new_list.append(copy.deepcopy(pop_sorted[i-1]))
        else:
            # En caso de fallo, tomar el primero (aunque esto no debería ocurrir)
            new_list.append(copy.deepcopy(pop_sorted[0]))
    
    return new_list

def crossover(pop):
    N = len(pop)
    sizeC = pop[0].N
    
    for i1 in range(0, N-1, 2):
        if random() > 0.8:
            continue
            
        i2 = i1 + 1
        if i2 >= N:
            break
            
        alelo1 = randint(0, sizeC*6 - 1)
        alelo2 = randint(alelo1 + 1, min(alelo1 + sizeC*6//2, sizeC*6))
        
        for i in range(alelo1, alelo2):
            if random() > 0.5:
                continue
            pop[i1].genotype[i], pop[i2].genotype[i] = pop[i2].genotype[i], pop[i1].genotype[i]

def mutation(pop):
    size = pop[0].N * 6 - 1
    
    # No mutar al mejor individuo (índice 0)
    for i in range(1, len(pop)):
        if random() > 0.2:
            continue
            
        # Mutar múltiples genes con baja probabilidad
        num_mutations = max(1, int(random() * 3))  # 1-3 mutaciones
        for _ in range(num_mutations):
            pos = randint(0, size)
            pop[i].genotype[pos] = randint(0, 9)

def genetic_simulation(func, xl, xh, N, M, fxl, fxh, cores=8):
    pop = createPop(M, xl, xh)
    all_data = []
    best_fitness = 0
    best_individual = None
    
    for gen in range(N):
        # Evaluar la población
        current_best, gen_data = update_fitness(func, pop, fxl, fxh, cores)
        
        # Recopilar datos si están disponibles
        if gen_data:
            all_data.extend(gen_data)
        
        # Actualizar el mejor global si es necesario
        if current_best.fitness > best_fitness:
            best_fitness = current_best.fitness
            best_individual = copy.deepcopy(current_best)
        
        # Operadores genéticos
        pop = selection(pop)
        crossover(pop)
        mutation(pop)
        
        # Actualizar fenotipos
        for ind in pop:
            ind.toPhenotype(xl, xh)
    
    # Evaluación final para verificar si hay mejoras
    final_best, final_data = update_fitness(func, pop, fxl, fxh, cores)
    
    if final_data:
        all_data.extend(final_data)
    
    if final_best.fitness > best_fitness:
        best_individual = final_best
    
    # Preparar resultados
    y_value = func(best_individual.phenotype)
    if isinstance(y_value, tuple):
        y_value = y_value[0]
    
    return (
        best_individual.phenotype,
        y_value,
        all_data
    )