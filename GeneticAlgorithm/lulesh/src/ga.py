import json, copy, random, os, logging
import numpy as np
from src import utilities as utilities

import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import naivega as nga

# generate initial population assigning random type
def gen_ini_pop(original_json_data, output_filename, initial_pop):
    json_form = {}
    initial_results = []

    for key, value in original_json_data.items():
        original_value = value.copy()

        if key.startswith("call") and isinstance(value.get("type"), list):
            new_type = utilities.choose_random_type()
            new_type_array = [new_type] * len(value["type"])
            original_value["type"] = new_type_array
        elif " " in original_value["type"]:
            chosen_type = utilities.choose_random_type()
            original_type_parts = original_value["type"].split(' ')
            original_type_parts[0] = chosen_type
            original_value["type"] = ' '.join(original_type_parts)
        else:
            chosen_type = utilities.choose_random_type()
            original_value["type"] = chosen_type

        json_form[key] = original_value
        initial_results.append([key, value["name"], original_value["type"]])

    with open(output_filename, 'w') as outfile:
        json.dump(json_form, outfile, indent=4)

    initial_pop.append(initial_results)

# calculate fitness for evaluation
def cal_fitness(original_score, pop_runtime):
    fitness = (original_score - pop_runtime) / original_score
    return fitness

# Select high fitness individuals for mating
def select_mating_pool(runtimes, pop, num_parents, original_score):
    fitness_scores = [cal_fitness(original_score, runtime) for runtime in runtimes]
    
    # Find indices of top num_parents individuals
    top_indices = np.argsort(fitness_scores)[-num_parents:]

    # Select top individuals from the population
    parents = [pop[index] for index in top_indices]

    return parents

# reproduct using parents gene
def crossover(pop):
    num_individuals = len(pop)
    offspring_crossover = []

    for i in range(num_individuals):
        parent = pop[i]
        next_parent = pop[(i + 1) % num_individuals]

        offspring1 = copy.deepcopy(parent)
        offspring2 = copy.deepcopy(next_parent)

        # set crossover point 1/2th of a parent
        crossover_point = len(parent) // 2

        offspring1[:crossover_point] = next_parent[:crossover_point]
        offspring2[:crossover_point] = parent[:crossover_point]

        offspring_crossover.extend([offspring1, offspring2])

    return offspring_crossover

def random_crossover(pop):
    num_individuals = len(pop)
    offspring_crossover = []

    # Select unique pairs of parents randomly
    parent_pairs = random.choices(pop, k=num_individuals * 2)

    # Iterate over pairs of parents
    for i in range(0, len(parent_pairs), 2):
        parent = parent_pairs[i]
        next_parent = parent_pairs[i + 1]

        offspring1 = copy.deepcopy(parent)
        offspring2 = copy.deepcopy(next_parent)

        # set crossover point 1/2th of a parent
        crossover_point = len(parent) // 2

        # set crossover point as a random value between 0 and len(parent)
        # crossover_point = random.randint(0, len(parent))

        offspring1[:crossover_point] = next_parent[:crossover_point]
        offspring2[:crossover_point] = parent[:crossover_point]

        offspring_crossover.extend([offspring1, offspring2])

    return offspring_crossover

def tournament_selection(runtimes, pop, original_score):
    fitness_scores = [cal_fitness(original_score, runtime) for runtime in runtimes]

    # Find indices of top individuals
    top_indices = np.argsort(fitness_scores)[-len(pop):]

    # Select first and second individuals from the population
    parent1 = pop[top_indices[0]]
    parent2 = pop[top_indices[1]]

    num_individuals = len(pop)
    offspring_crossover = []
    selected_indices = []

    for i in range(num_individuals):
        parent = parent1 if i < num_individuals // 2 else parent2

        available_indices = [i for i in range(len(pop)) if i not in selected_indices]
        random_index = random.choice(available_indices)
        selected_indices.append(random_index)
        random_parent = pop[random_index]

        offspring1 = copy.deepcopy(parent)
        offspring2 = copy.deepcopy(random_parent)

        crossover_point = len(parent) // 2

        offspring1[:crossover_point] = random_parent[:crossover_point]
        offspring2[:crossover_point] = parent[:crossover_point]

        offspring_crossover.extend([offspring1, offspring2])

    return offspring_crossover

# mutate random individual's random gene
def mutation(offspring_crossover, num_indi_mut, num_gene_mut):
    mutated_offspring = copy.deepcopy(offspring_crossover)

    for _ in range(num_indi_mut):
        indi_idx = random.randint(0, len(mutated_offspring) - 1)

        for _ in range(num_gene_mut):
            gene_idx = random.randint(0, len(mutated_offspring[indi_idx]) - 1)
            mutated_offspring[indi_idx][gene_idx][2] = utilities.choose_random_type()

    return mutated_offspring

# Find the index of the elite individual in the current generation
def search_elite(results, runtimes, pop):
    elite_individual = None
    elite_runtime = 0
    elite_return_index = -1
    
    elite_indices = [i for i, (result, _) in enumerate(results) if result == 1]

    if elite_indices:
        elite_index = min(elite_indices, key=lambda i: runtimes[i])
        if elite_index > 0:
            elite_individual = pop[elite_index-1]
            elite_runtime = runtimes[elite_index-1]
            elite_return_index = elite_index
            print(f"Elite_individual, Config {elite_index} Runtime: {runtimes[elite_index]} Result: {results[elite_index][0]}")
            logging.info(f"Elite_individual, Config {elite_index} Runtime: {runtimes[elite_index]} Result: {results[elite_index][0]}")
        else:
            elite_individual = None

    return elite_individual, elite_runtime, elite_return_index  