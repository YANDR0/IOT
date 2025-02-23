from math import cos, pi, e
from random import random, uniform
from time import time


### Test functions ###
def rosenbrock(x, dim = 2):
    fx = 0
    for i in range(dim - 1):
        fx += 100 * pow(x[i + 1] - x[i] * x[i], 2) + pow(1 - x[i], 2)
    return fx

def rastrigin(x, dim = 2):
    fx = 0
    for i in range(dim):
        fx += x[i] * x[i] - 10 * cos(2 * pi * x[0])
    return 10 * dim + fx

def styblinski(x, dim = 2):
    fx = 0
    for i in range(dim):
        fx += pow(x[i], 4) - 16 * pow(x[i], 2) + 5 * x[i]
    return fx / 2

def ackley(x, dim = 2):
    sum1 = 0
    sum2 = 0
    for i in range(dim):
        sum1 += x[i] ** 2
        sum2 += cos(2 * pi * x[i])
    return (
        -20 * pow(e, -0.2 * pow(1 / dim * sum1, 0.5)) - pow(e, 1 / dim * sum2) + 20 + e
    )


# -------------------------------------------------------------


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
        return [(h - l) * (1 - fitness) for l, h in zip(self.xLow, self.xHigh)]

    def optimizeRange(self, n, data = None):
        x = VectorOperations.ramdomRange(self.xLow, self.xHigh) if not data else data['x']
        y = self.func(x) if not data else data['traffic_flow']
        Dx = self.getDx(0)
        dx = HillClimbing.ranIncrement(Dx)

        for _ in range(n):
            tempX = VectorOperations.sumVector(x, dx)
            tempY = self.func(tempX)
            if tempY < y:
                x = tempX
                y = tempY
                Dx = self.getDx(1 / (1 + y))
            else:
                dx = HillClimbing.ranIncrement(Dx)

        return x, y


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
        self.bestY = Swarm.func(self.x)

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
        y = Swarm.func(self.x)
        if y >= self.bestY:
            return
        self.bestY = y
        self.bestX = self.x
        if y >= Swarm.BestY:
            return
        Swarm.BestY = y
        Swarm.BestX = self.x


# -------------------------------------------------------------


### Main ###
def swarm_simulation(func, xLow, xHigh, m, n, data):
    swarm = Swarm(func, 0.001, 0.1, 0.1, xLow, xHigh)
    particles = [swarm.createParticle() for _ in range(m)]
    if(data):
        swarm.BestX = data['x']
        swarm.BestY = data['traffic_flow']
        
    for _ in range(n):
        for p in particles:
            p.updateParticle(swarm)

    return swarm


def hill_simulation(func, xLow, xHigh, n, data):
    hill = HillClimbing(func, xLow, xHigh)
    return hill.optimizeRange(n, data)


def randomMin(func, xLow, xHigh, n, data):
    yMin = float("inf") if not data else data['traffic_flow']
    dim = len(xLow)
    xMin = [0 for _ in range(dim)] if not data else data['x']

    for i in range(n):
        x = VectorOperations.ramdomRange(xLow, xHigh)
        num = func(x)
        xMin = x if num < yMin else xMin
        yMin = min(num, yMin)

    return xMin, yMin


###########
if __name__ == "__main__":
    xLow = (-5, -5, -5)
    xHigh = (5, 5, 5)

    #'''
    print("Random")
    start = time()
    x, y = randomMin(rosenbrock, xLow, xHigh, 100_000)
    print("Rosenbrock", x, y)
    x, y = randomMin(rastrigin, xLow, xHigh, 100_000)
    print("Rastrigin", x, y)
    x, y = randomMin(styblinski, xLow, xHigh, 100_000)
    print("Styblinski", x, y)
    x, y = randomMin(ackley, xLow, xHigh, 100_000)
    print("Ackley", x, y)
    print("- Time: ", time() - start)
    #'''

    #'''
    print("\nHill Climbing")
    start = time()
    x, y = hill_simulation(rosenbrock, xLow, xHigh, 100_000)
    print("Rosenbrock", x, y)
    x, y = hill_simulation(rastrigin, xLow, xHigh, 100_000)
    print("Rastrigin", x, y)
    x, y = hill_simulation(styblinski, xLow, xHigh, 100_000)
    print("Styblinski", x, y)
    x, y = hill_simulation(ackley, xLow, xHigh, 100_000)
    print("Ackley", x, y)
    print("- Time: ", time() - start)
    #'''

    #'''
    print("\nSwarm")
    start = time()
    s = swarm_simulation(rosenbrock, xLow, xHigh, 100, 1000)
    print("Rosenbrock", s.BestX, s.BestY)
    s = swarm_simulation(rastrigin, xLow, xHigh, 100, 1000)
    print("Rastrigin", s.BestX, s.BestY)
    s = swarm_simulation(styblinski, xLow, xHigh, 100, 1000)
    print("Styblinski", s.BestX, s.BestY)
    s = swarm_simulation(ackley, xLow, xHigh, 100, 1000)
    print("Ackley", s.BestX, s.BestY)
    print("- Time: ", time() - start)
    #'''
