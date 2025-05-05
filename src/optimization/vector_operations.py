from random import uniform

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