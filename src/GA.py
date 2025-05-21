import random
import numpy as np

def generate_random_route(n):
    route = list(range(1, n))  # loại thành phố 0 (gốc)
    random.shuffle(route)
    return [0] + route  # luôn xuất phát từ 0

def compute_route_distance(route, distances):
    distance = 0
    for i in range(len(route) - 1):
        distance += distances[route[i]][route[i + 1]]
    return distance

def inversion_mutate(route, mutation_rate):
    if random.random() < mutation_rate:
        start, end = sorted(random.sample(range(1, len(route)), 2))
        route[start:end] = reversed(route[start:end])
    return route

def scramble_mutate(route, mutation_rate):
    if random.random() < mutation_rate:
        point1 = random.randint(1, len(route) - 2)
        point2 = random.randint(point1 + 1, len(route) - 1)
        segment = route[point1:point2]
        random.shuffle(segment)
        route = route[:point1] + segment + route[point2:]
    return route

def swap_mutate(route, mutation_rate):
    for i in range(1, len(route)):
        if random.random() < mutation_rate:
            j = random.randint(1, len(route) - 1)
            route[i], route[j] = route[j], route[i]
    return route

def insertion_mutate(route, mutation_rate):
    if random.random() < mutation_rate:
        i, j = sorted(random.sample(range(1, len(route)), 2))
        city = route.pop(j)
        route.insert(i, city)
    return route

def mutate(route, mutation_rate, algorithm='swap'):
    if algorithm == 'swap':
        return swap_mutate(route, mutation_rate)
    elif algorithm == 'scramble':
        return scramble_mutate(route, mutation_rate)
    elif algorithm == 'inversion':
        return inversion_mutate(route, mutation_rate)
    elif algorithm == 'insertion':
        return insertion_mutate(route, mutation_rate)
    else:
        return route

def order_crossover(parent1, parent2):
    split = random.randint(1, len(parent1) - 1)
    child1 = parent1[:split] + [city for city in parent2 if city not in parent1[:split]]
    child2 = parent2[:split] + [city for city in parent1 if city not in parent2[:split]]
    return child1, child2

def single_point_crossover(parent1, parent2):
    point = random.randint(1, len(parent1) - 1)
    c1 = parent1[:point] + [x for x in parent2 if x not in parent1[:point]]
    c2 = parent2[:point] + [x for x in parent1 if x not in parent2[:point]]
    return c1, c2

def two_point_crossover(parent1, parent2):
    p1, p2 = sorted(random.sample(range(1, len(parent1)), 2))
    def make_child(p1s, p2s):
        mid = [city for city in p2s if city not in p1s[:p1] + p1s[p2:]]
        return p1s[:p1] + mid + p1s[p2:]
    return make_child(parent1, parent2), make_child(parent2, parent1)

def uniform_crossover(parent1, parent2):
    child1 = []
    child2 = []
    for i in range(len(parent1)):
        if random.random() < 0.5:
            child1.append(parent1[i])
            child2.append(parent2[i])
        else:
            child1.append(parent2[i])
            child2.append(parent1[i])
    return repair(child1), repair(child2)

def repair(route):
    seen = set()
    new_route = []
    for city in route:
        if city not in seen:
            new_route.append(city)
            seen.add(city)
    missing = [c for c in range(len(route)) if c not in seen]
    return new_route + missing

def crossover(p1, p2, algorithm='order'):
    if algorithm == 'order':
        return order_crossover(p1, p2)
    elif algorithm == 'single_point':
        return single_point_crossover(p1, p2)
    elif algorithm == 'two_point':
        return two_point_crossover(p1, p2)
    elif algorithm == 'uniform':
        return uniform_crossover(p1, p2)
    else:
        return p1[:], p2[:]

def elitism_selection(population, fitness_scores):
    selected = []
    fs = fitness_scores.copy()
    for _ in range(len(population) // 2):
        i = fs.index(min(fs))
        selected.append(population[i])
        fs[i] = float('inf')
    return selected

def tournament_selection(population, fitness_scores, k=3):
    selected = []
    for _ in range(len(population) // 2):
        indices = random.sample(range(len(population)), k)
        best = min(indices, key=lambda i: fitness_scores[i])
        selected.append(population[best])
    return selected

def rank_selection(population, fitness_scores):
    sorted_pop = [x for _, x in sorted(zip(fitness_scores, population))]
    probs = 1 / (np.arange(1, len(population) + 1))
    probs /= probs.sum()
    cum_probs = np.cumsum(probs)
    selected = []
    for _ in range(len(population) // 2):
        r = random.random()
        for i, p in enumerate(cum_probs):
            if r <= p:
                selected.append(sorted_pop[i])
                break
    return selected

def roulette_wheel_selection(population, fitness_scores):
    max_fit = max(fitness_scores)
    adj_fit = [max_fit - f for f in fitness_scores]
    total = sum(adj_fit)
    selected = []
    for _ in range(len(population) // 2):
        r = random.uniform(0, total)
        acc = 0
        for i, f in enumerate(adj_fit):
            acc += f
            if acc >= r:
                selected.append(population[i])
                break
    return selected

def selection(population, fitness_scores, algorithm='elitism'):
    if algorithm == 'elitism':
        return elitism_selection(population, fitness_scores)
    elif algorithm == 'tournament':
        return tournament_selection(population, fitness_scores)
    elif algorithm == 'rank':
        return rank_selection(population, fitness_scores)
    elif algorithm == 'roulette_wheel':
        return roulette_wheel_selection(population, fitness_scores)
    else:
        return population[:2]


def fitness(population, distance_matrix):
    return [compute_route_distance(route + [route[0]], distance_matrix) for route in population]

def genetic_algorithm(n_cities, distances, population_size=100, generations=100,
                      mutation_rate=0.01, mutation_algorithm='swap',
                      selection_algorithm='elitism', crossover_algorithm='order'):

    population = [generate_random_route(n_cities) for _ in range(population_size)]
    fitness_history = []

    for _ in range(generations):
        fitness_scores = fitness(population, distances)
        fitness_history.append(min(fitness_scores))

        selected = selection(population, fitness_scores, selection_algorithm)
        offspring = []

        while len(offspring) < population_size:
            p1, p2 = random.sample(selected, 2)
            c1, c2 = crossover(p1, p2, crossover_algorithm)
            offspring.append(mutate(c1, mutation_rate, mutation_algorithm))
            offspring.append(mutate(c2, mutation_rate, mutation_algorithm))

        population = offspring[:population_size]

    final_fitness = fitness(population, distances)
    best_idx = np.argmin(final_fitness)
    best_route = population[best_idx] + [population[best_idx][0]]

    return {
        'route': [city + 1 for city in best_route],
        'distance': final_fitness[best_idx],
        'fitness': fitness_history
    }

def solve(problem,
          population_size=100,
          generations=100,
          mutation_rate=0.01,
          mutation_algorithm='swap',
          crossover_algorithm='single_point',
          selection_algorithm='tournament'):
    
    n_cities = len(problem)
    result = genetic_algorithm(
        n_cities=n_cities,
        distances=problem,
        population_size=population_size,
        generations=generations,
        mutation_rate=mutation_rate,
        mutation_algorithm=mutation_algorithm,
        selection_algorithm=selection_algorithm,
        crossover_algorithm=crossover_algorithm
    )
    return result['distance'], result['route'], result['fitness']

#--------------------------------------------- RLGA ------------------------------------
def solve_rlga(problem,
               population_size=100,
               generations=100,
               mutation_rate=0.01,
               crossover_algorithm='single_point',
               selection_algorithm='tournament'):
    
    n_cities = len(problem)
    mutation_algorithms = ['swap', 'scramble', 'inversion', 'insertion']

    def rlga_mutate(route, base_rate):
        algo = random.choice(mutation_algorithms)
        return mutate(route, base_rate, algo)

    def rlga_genetic_algorithm():
        population = [generate_random_route(n_cities) for _ in range(population_size)]
        fitness_history = []

        for _ in range(generations):
            fitness_scores = fitness(population, problem)
            fitness_history.append(min(fitness_scores))
            selected = selection(population, fitness_scores, selection_algorithm)
            offspring = []

            while len(offspring) < population_size:
                p1, p2 = random.sample(selected, 2)
                c1, c2 = crossover(p1, p2, crossover_algorithm)
                offspring.append(rlga_mutate(c1, mutation_rate))
                offspring.append(rlga_mutate(c2, mutation_rate))

            population = offspring[:population_size]

        final_fitness = fitness(population, problem)
        best_idx = np.argmin(final_fitness)
        best_route = population[best_idx] + [population[best_idx][0]]

        return {
            'route': [city + 1 for city in best_route],
            'distance': final_fitness[best_idx],
            'fitness': fitness_history
        }

    result = rlga_genetic_algorithm()
    return result['distance'], result['route'], result['fitness']


#--------------------------------------------- GASA ------------------------------------
def simulated_annealing(route, distances, initial_temp=100, cooling_rate=0.995, min_temp=1e-3):
    current = route[:]
    best = current[:]
    current_distance = compute_route_distance(current + [current[0]], distances)
    best_distance = current_distance
    temp = initial_temp

    while temp > min_temp:
        i, j = sorted(random.sample(range(1, len(route)), 2))
        neighbor = current[:]
        neighbor[i], neighbor[j] = neighbor[j], neighbor[i]
        neighbor_distance = compute_route_distance(neighbor + [neighbor[0]], distances)

        delta = neighbor_distance - current_distance
        if delta < 0 or random.random() < np.exp(-delta / temp):
            current = neighbor
            current_distance = neighbor_distance
            if current_distance < best_distance:
                best = current
                best_distance = current_distance

        temp *= cooling_rate

    return best

def solve_gasa(problem,
               population_size=100,
               generations=100,
               mutation_rate=0.01,
               mutation_algorithm='swap',
               crossover_algorithm='single_point',
               selection_algorithm='tournament'):
    
    n_cities = len(problem)

    population = [generate_random_route(n_cities) for _ in range(population_size)]
    fitness_history = []

    for _ in range(generations):
        fitness_scores = fitness(population, problem)
        fitness_history.append(min(fitness_scores))
        selected = selection(population, fitness_scores, selection_algorithm)
        offspring = []

        while len(offspring) < population_size:
            p1, p2 = random.sample(selected, 2)
            c1, c2 = crossover(p1, p2, crossover_algorithm)
            offspring.append(mutate(c1, mutation_rate, mutation_algorithm))
            offspring.append(mutate(c2, mutation_rate, mutation_algorithm))

        population = offspring[:population_size]

        # Simulated Annealing cải tiến cá thể tốt nhất
        best_idx = np.argmin(fitness(population, problem))
        improved = simulated_annealing(population[best_idx], problem)
        population[best_idx] = improved

    final_fitness = fitness(population, problem)
    best_idx = np.argmin(final_fitness)
    best_route = population[best_idx] + [population[best_idx][0]]

    return final_fitness[best_idx], [city + 1 for city in best_route], fitness_history
