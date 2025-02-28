import sys, os, json, logging, time, subprocess
from src import utilities as utilities
from src import ga as ga
import numpy as np
import pandas as pd

benchmark = sys.argv[1]

target_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), benchmark))
sys.path.append(target_dir)
import runner

TIME_OUT = int(sys.argv[3])
EPSILON = int(sys.argv[4])
CLASS = sys.argv[5]
RESULTSDIR = runner.setup(benchmark, TIME_OUT, EPSILON, CLASS)
SEARCHEDDIR = f"{RESULTSDIR}/searched"


def main():
    global benchmark
    original_conf_file = sys.argv[2]
    initial_population = 100
    generation_num = 50

    if not os.path.exists(RESULTSDIR):
        os.makedirs(RESULTSDIR)
    elif os.path.exists(RESULTSDIR):
        os.system(f"rm -r {RESULTSDIR}/*.json")
        os.system(f"rm -r gen_*_config_*.json")
    
    logging.basicConfig(filename='{}/naivega-{}.log'.format(RESULTSDIR, time.strftime("%Y%m%d-%H%M%S")), level=logging.DEBUG)

    # delete log file if exists
    try:
        os.remove("log.dd")
    except OSError:
        pass

    initial_pop = []
    population = []
    mating_pool = []
    elite_individual = None
    config_history = []
    results = []
    runtimes = []
    elite_history = []
    current_configs_vec = []

    runner.run_orig_config(original_conf_file)
    original_score = utilities.get_dynamic_score()
    print(f"original_score: {original_score}")
    logging.info(f"original_score: {original_score}")

    try:
        with open(original_conf_file, 'r') as original_json_file:
            original_json_data = json.load(original_json_file)

            # generate initial population and save that as json file
            for index in range(initial_population):
                output_filename = f"gen_0_config_{index}.json"
                ga.gen_ini_pop(original_json_data, output_filename, initial_pop)

            # convert population format to perform crossover and mutation
            population = [utilities.convert_format(pop) for pop in initial_pop]

            # reproduction of next generation based on the fitness 
            for generation in range(generation_num):
                if len(population) > 0 and len(population) <= 2:
                    generation_num = generation
                    break
                
                results = [runner.run_config(generation, i) for i in range(len(population))]
                runtimes = [runtime for _, runtime in results]
                # Find the elite individual in the current generation
                elite_individual = ga.search_elite(results, runtimes, population)

                # Add the elite individual to the history
                elite_history.append({
                    'generation': generation,
                    'config_num': elite_individual[2],
                    'elite_individual': elite_individual[0],
                })

                # Print or log the elite individual and its history
                print(f"Generation {generation}, Elite individual: {elite_individual[0]}")
                logging.info(f"Generation {generation}, Elite individual: {elite_individual[0]}")
                print(f"Elite history: {elite_history}")
                logging.info(f"Elite history: {elite_history}")

                # selection of high fitness individual as parents
                num_parents = int(len(population) / 2)
                mating_pool = ga.select_mating_pool(runtimes, population, num_parents, original_score)
                
                # crossover using parents
                offspring_crossover = ga.crossover(mating_pool)

                # mutation among the regenerated population
                num_indi_mut = int(len(offspring_crossover) * 0.08)
                num_gene_mut = max(int(len(offspring_crossover[0]) * 0.02),1)
                population = ga.mutation(offspring_crossover, num_indi_mut, num_gene_mut)

                # duplication checker
                current_configs_vec = [utilities.parse_json(population[i]) for i in range(len(population))]                
                duplicate_indices = [i for i, config in enumerate(current_configs_vec) if config in config_history]

                # remove duplication
                population = [population[i] for i in range(len(population)) if i not in duplicate_indices]
                
                # record history for checking duplication 
                unique_configs = [config for config in current_configs_vec if config not in config_history]
                config_history.extend(unique_configs)

                if elite_individual[0] is not None and elite_individual[0] not in population:
                    population.append(elite_individual[0])
                    print(f"Elite individual added to the {generation+1}th generation")
                    logging.info(f"Elite individual added to the {generation+1}th generation")

                # convert population format from array to json for execution
                for index, mutated_data in enumerate(population):
                    output_filename = f"gen_{generation + 1}_config_{index}.json"
                    utilities.transform_json(original_conf_file, output_filename, mutated_data)
                
            # Last Generation execution 
            results = [runner.run_config(generation_num, i) for i in range(len(population))]
            runtimes = [runtime for _, runtime in results]
            elite_individual = ga.search_elite(results, runtimes, population)

            elite_history.append({
                'generation': generation_num,
                'config_num': elite_individual[2],
                'elite_individual': elite_individual[0],
            })

            # Print or log the final elite individual and its history
            print(f"Final elite individual: {elite_individual[0]}")
            logging.info(f"Final elite individual: {elite_individual[0]}")
            print(f"Final elite history: {elite_history}")
            logging.info(f"Final elite history: {elite_history}")

            # Compare elite individuals from the whole history
            for i in range(1, len(elite_history)):
                if elite_history[i]['elite_individual'] != elite_history[i-1]['elite_individual']:
                    print(f"Elite individual changed at generation {elite_history[i]['generation']}")
                else:
                    print(f"Elite individual kept since generation {elite_history[i-1]['generation']}")                    

            if elite_individual[0] is not None:
                with open('{}/best_speedup_{}_{}.txt'.format(RESULTSDIR, benchmark, str(elite_individual[2])), 'w') as f:
                    speedup = ((original_score - elite_individual[1]) / original_score) + 1
                    print(speedup, file=f)
                    print(f"Original Score: {original_score} Elite Score: {elite_individual[1]}")
                    logging.info(f"Original Score: {original_score} Elite Score: {elite_individual[1]}")
                    print(f"Speedup: {(speedup - 1)*100}%") 
                    logging.info(f"Speedup: {(speedup - 1)*100}%")
            else:
                print("No elite individual found")
                logging.info("No elite individual found")

            # Print the runtime for the last generation
            for i, runtime in enumerate(runtimes):
                print(f"Last Generation, Config {i} Runtime: {runtime} Result: {results[i][0]}")
                logging.info(f"Last Generation, Config {i} Runtime: {runtime} Result: {results[i]}")
            
            print(f"Visited Individuals: {len(config_history)}")
            logging.info(f"Visited Individuals: {len(config_history)}")

    except json.JSONDecodeError:
        print(f"Error: Unable to decode JSON error.")
    
    runner.df.to_csv(RESULTSDIR+'/df-configs.csv')


if __name__ == "__main__":
  main()
