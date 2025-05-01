from multiprocessing import Pool
from .vector_operations import VectorOperations

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
