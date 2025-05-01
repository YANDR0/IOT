from .vector_operations import VectorOperations
from random import random

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
