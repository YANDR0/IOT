from random import random, uniform, randint
import copy
import functools
from multiprocessing import Pool

### Vector operations
class VectorOperations:
    @staticmethod
    def sumVector(vector1, vector2, substract=False):
        sign = -1 if substract else 1
        return [i + (j) * sign for i, j in zip(vector1, vector2)]

    @staticmethod
    def multiplyScalar(vector, num):
        return [i * num for i in vector]

    @staticmethod
    def ramdomRange(low, high):
        return [uniform(low[i], high[i]) for i in range(len(low))]

# -------------------------------------------------------------

### Random 

def _random_task(args):
    func, xLow, xHigh = args
    x = VectorOperations.ramdomRange(xLow, xHigh)
    y, data = func(x)  # Capturar datos
    return x, y, data

def random_simulation(func, xLow, xHigh, n, data=None, cores=8):
    tasks = [(func, xLow, xHigh) for _ in range(n)]
    with Pool(processes=cores) as pool:
        results = pool.map(_random_task, tasks)
    
    all_data = [result[2] for result in results]
    
    if data:
        all_data.append(data)
        results.append((data['x'], data['y'], data))
    
    xMin, yMin, _ = min(results, key=lambda xy: xy[1])
    
    return xMin, yMin, all_data


### Hill Climbing
class HillClimbing:
    def __init__(self, func, xLow, xHigh):
        self.func = func
        self.xLow = xLow
        self.xHigh = xHigh
        self.dim = len(xLow)

    @staticmethod
    def ranIncrement(Dx):
        return [-0.5 * dx + random() * dx for dx in Dx]

    def getDx(self, fitness):
        return [(h - l) * (1 - fitness) for l, h in zip(self.xLow, self.xHigh)]  # noqa: E741

    def optimizeRange(self, n, data = None):
        x = VectorOperations.ramdomRange(self.xLow, self.xHigh) if not data else data['x']
        y = self.func(x)[0] if not data else data['y']
        Dx = self.getDx(0)
        dx = HillClimbing.ranIncrement(Dx)

        for _ in range(n):
            tempX = VectorOperations.sumVector(x, dx)
            tempY = self.func(tempX)[0]
            if tempY < y:
                x = tempX
                y = tempY
                Dx = self.getDx(1 / (1 + y))
            else:
                dx = HillClimbing.ranIncrement(Dx)

        return x, y

# func = function, xLow and xHigh = LimitX, n = simulations, data = previous results
def hill_simulation(func, xLow, xHigh, n, data):
    hill = HillClimbing(func, xLow, xHigh)
    return hill.optimizeRange(n, data)

# -------------------------------------------------------------

### Swarm algoritm

# Variables de particulas o
class Swarm:
    # Crear enjambre
    def __init__(self, func, w, c1, c2, xLow, xHigh):
        self.BestX = None
        self.BestY = None
        self.func = func
        self.W = w
        self.C1 = c1
        self.C2 = c2
        self.xLow = xLow
        self.xHigh = xHigh
        self.dim = len(xLow)

    # Creación de particula vinculada al enjambre
    def createParticle(self):
        return Particle(self)


# Particulas
class Particle:
    # Creación de una partícula en base a un rango y un enjambre
    def __init__(self, Swarm: Swarm):
        self.x = VectorOperations.ramdomRange(Swarm.xLow, Swarm.xHigh)
        self.v = [random() * 2 - 1 for _ in range(Swarm.dim)]
        self.bestX = self.x
        self.bestY = Swarm.func(self.x)[0]

        # Check if new position is a best
        if not Swarm.BestY or self.bestY < Swarm.BestY:
            Swarm.BestX = self.x
            Swarm.BestY = self.bestY

    # String representation
    def __repr__(self):
        return f"x: {str(self.x)}, v: {str(self.v)}"

    # Actualización de la particla
    def updateParticle(self, Swarm: Swarm):
        # Obtener valores
        r1 = random() * Swarm.C1
        r2 = random() * Swarm.C2
        currSpeed = self.v

        # Calcular la nueva velocidad y posición
        for i in range(Swarm.dim):
            self.v[i] = (
                Swarm.W * self.v[i]
                + Swarm.C1 * r1 * (self.bestX[i] - self.x[i])
                + Swarm.C2 * r2 * (Swarm.BestX[i] - self.x[i])
            )
            self.x[i] = currSpeed[i] + self.x[i]

        # Revisar si la nueva posición es un mínimo
        y = Swarm.func(self.x)[0]
        if y >= self.bestY:
            return
        self.bestY = y
        self.bestX = self.x
        if y >= Swarm.BestY:
            return
        Swarm.BestY = y
        Swarm.BestX = self.x

# func = function, xLow and xHigh = LimitX, m size simulation, n simulations, data = previous results
def swarm_simulation(func, xLow, xHigh, m, n, data):
    swarm = Swarm(func, 0.001, 0.1, 0.1, xLow, xHigh)
    particles = [swarm.createParticle() for _ in range(m)]
    if(data):
        swarm.BestX = data['x']
        swarm.BestY = data['y']
        
    for _ in range(n):
        for p in particles:
            p.updateParticle(swarm)

    return swarm

# -------------------------------------------------------------
### Genetic

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