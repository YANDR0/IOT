from random import random, uniform, randint
import copy
import functools
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
    y, data = func(phenotype)  # Ahora capturamos los datos de la simulación
    fval = 1 - (y - fxl) / (fxh - fxl) if (fxh - fxl) != 0 else 0
    return fval, data

def evaluate_fitness_parallel(func, pop, fxl, fxh, cores=8):
    tasks = [(ind.phenotype, func, fxl, fxh) for ind in pop]
    
    with Pool(processes=cores) as pool:
        results = pool.map(_evaluate_task, tasks)
    
    fitnesses = [r[0] for r in results]
    all_data = [r[1] for r in results]
    return fitnesses, all_data

def update_fitness(func, pop: list[Individual], fxl, fxh, cores=8):
    fitnesses, all_data = evaluate_fitness_parallel(func, pop, fxl, fxh, cores)
    
    best = None
    for ind, fval in zip(pop, fitnesses):
        ind.fitness = fval
        if best is None or ind.fitness > best.fitness:
            best = copy.deepcopy(ind)
    
    return best, all_data

def selection(pop: list[Individual]):
    pop.sort(key=lambda x: x.fitness)
    N = len(pop)
    for i in range(N):
        pop[i].expected_value = 0.9 + (1.1 - 0.9) * i / (N - 1)

    new_list = [copy.deepcopy(pop[-1])]
    
    for _ in range(N-1):
        pick = uniform(0, sum(ind.expected_value for ind in pop))
        current = 0
        for ind in pop:
            current += ind.expected_value
            if current >= pick:
                new_list.append(copy.deepcopy(ind))
                break
    
    return new_list

def crossover(pop: list[Individual]):
    N = len(pop)
    sizeC = pop[0].N
    for i1 in range(2, N, 2):
        if random() > 0.8:
            continue
        i2 = i1 + 1
        if i2 >= N:
            break

        alelo1 = randint(0, sizeC*6 - 1)
        alelo2 = randint(alelo1 + 1, sizeC*6)

        for i in range(alelo1, alelo2):
            if random() > 0.5:
                continue
            pop[i1].genotype[i], pop[i2].genotype[i] = pop[i2].genotype[i], pop[i1].genotype[i]

def mutation(pop: list[Individual]):
    size = pop[0].N * 6 - 1
    for i in range(1, len(pop)):
        if random() > 0.2:
            continue
        pos = randint(0, size)
        pop[i].genotype[pos] = randint(0, 9)

def genetic_simulation(func, xl, xh, N, M, fxl, fxh, cores=8):
    pop = createPop(M, xl, xh)
    all_data = []
    bf = 0
    best_individual = None
    
    for _ in range(N):
        best, gen_data = update_fitness(func, pop, fxl, fxh, cores)
        all_data.extend(gen_data)
        
        if best.fitness > bf:
            bf = best.fitness
            best_individual = copy.deepcopy(best)
        
        pop = selection(pop)
        crossover(pop)
        mutation(pop)
        
        for ind in pop:
            ind.toPhenotype(xl, xh)
    
    # Última evaluación para asegurar el mejor
    final_best, final_data = update_fitness(func, pop, fxl, fxh, cores)
    all_data.extend(final_data)
    
    if final_best.fitness > bf:
        best_individual = final_best
    
    return (
        best_individual.phenotype,
        func(best_individual.phenotype)[0],  # Devuelve solo el valor y
        all_data
    )