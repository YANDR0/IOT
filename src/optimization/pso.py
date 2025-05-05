from .vector_operations import VectorOperations
from random import random

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