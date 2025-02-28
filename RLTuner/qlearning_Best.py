import sys, os, json, logging, time, copy
import numpy as np
from src import utilities as utilities
import pandas as pd
from collections import namedtuple

benchmark = sys.argv[1]
target_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), benchmark))
sys.path.append(target_dir)
print(f"target_dir: {target_dir}")
from runner import setup, run_config, run_orig_config

TIME_OUT = int(sys.argv[3])
B_EPSILON = sys.argv[4]
CLASS = sys.argv[5]
FAIL_RESTAT_FLAG = sys.argv[6]

EPSILON = 0.5   # greedy policy
ALPHA = 0.1     # learning rate
GAMMA = 0.95    # discount factor

ACTIONS = []
Data = namedtuple('state_config_map', ['state', 'config', 'config_vec', 'result', 'speedup', 'searched'])
RESULTSDIR = setup(benchmark, TIME_OUT, EPSILON, CLASS, B_EPSILON)


def gen_ini_state(original_json_data, output_filename, initial_config):
    json_form = {}
    initial_config = []

    for key, value in original_json_data.items():
        original_value = value.copy()

        if key.startswith("call") and isinstance(value.get("type"), list):
            new_type_array = ["double"] * len(value["type"])
            original_value["type"] = new_type_array
        elif " " in original_value["type"]:
            original_type_parts = original_value["type"].split(' ')
            original_type_parts[0] = "double"
            original_value["type"] = ' '.join(original_type_parts)
        else:
            original_value["type"] = "double"

        json_form[key] = original_value
        initial_config.append([key, value["function"], value["name"], original_value["type"]])

    with open(output_filename, 'w') as outfile:
        json.dump(json_form, outfile, indent=4)

    return initial_config


def build_q_table(actions):
    table = pd.DataFrame(
        np.zeros((1, len(actions))),
        columns = ['-'.join(action) for action in actions]
    )
    print(table)
    return table


def get_all_actions(initial_config):
    action_candidates = []

    for tunables in initial_config:
        key = tunables[0]
        function = tunables[1] if tunables[1] is not None else "None"
        variable_name = tunables[2]
        action_candidates.append([key, function, variable_name])

    return action_candidates


def choose_action(state, q_table, num_actions=1):
    state_actions = q_table.iloc[state, :]
    selected_actions = []

    while len(selected_actions) < num_actions:
        greedy_flag = np.random.uniform()
        if (greedy_flag > EPSILON) or ((state_actions == 0).all()):
            action_name = np.random.choice(['-'.join(action) for action in ACTIONS])
            if action_name in selected_actions:
                continue
            ACTIONS.remove(action_name.split('-'))
            selected_actions.append(action_name)
            print(f"non-greedy action_name: {action_name}")
            logging.info(f"non-greedy action_name: {action_name}")
        else:
            action_name = state_actions.idxmax()
            if action_name in selected_actions:
                continue
            selected_actions.append(action_name)
            print(f"greedy_action_name: {action_name}")
            logging.info(f"greedy_action_name: {action_name}")

    print(f"selected_actions: {selected_actions}")

    return selected_actions

def get_env_feedback(selected_actions, S, prev_config, original_conf_file, original_score, state_config_map, q_table):
    updated_config = []

    for A in selected_actions:
        action = A.split('-')
        key = action[0]
        function = action[1]
        variable_name = action[2]

        for i in range(len(prev_config)):
            if prev_config[i][1] is None:
                if prev_config[i][0] == key and prev_config[i][2] == variable_name:
                    if " " in prev_config[i][3]:
                        prev_config_parts = prev_config[i][3].split(' ')
                        prev_config_parts[0] = 'float'
                        prev_config[i][3] = ' '.join(prev_config_parts)
                    else:
                        prev_config[i][3] = 'float'
            else: 
                if prev_config[i][0] == key and prev_config[i][1] == function and prev_config[i][2] == variable_name:
                    if " " in prev_config[i][3]:
                        prev_config_parts = prev_config[i][3].split(' ')
                        prev_config_parts[0] = 'float'
                        prev_config[i][3] = ' '.join(prev_config_parts)
                    else:
                        prev_config[i][3] = 'float'
            if A == selected_actions[-1]:
                updated_config.append(prev_config[i])

    print("updated_config:")
    logging.info("updated_config:")
    for item in updated_config:
        print(item)
        logging.info(item)

    output_filename = f"updated_config.json"
    utilities.transform_json(original_conf_file, output_filename, updated_config)
   
    config_vec = utilities.parse_json(updated_config)
    config_vec_since = [tuple(data.config_vec) for state, data in state_config_map.items()]
    print(f"config_vec: {config_vec}")
    logging.info(f"config_vec: {config_vec}")

    if tuple(config_vec) not in config_vec_since:
        S_ = len(state_config_map)
        S = S_ + 1

        result, runtime = run_config(S)
        speedup = ((original_score - runtime) / original_score)
        
        state_config_map[S] = copy.deepcopy(Data(S, updated_config, config_vec, result, speedup, searched=False))
        S_ += 1
        q_table.loc[S_, :] = 0

    elif tuple(config_vec) in config_vec_since:
        for key, value in state_config_map.items():
            if tuple(value.config_vec) == tuple(config_vec):
                S_ = S
                speedup = value.speedup
                result = value.result
                S = value.state
                break

    next_config = prev_config 
    R = -1

    if speedup >= 0.3 and result == 1:
        next_config = updated_config
        R = 999
    
    elif speedup > 0 and result == 1:
        next_config = updated_config
        R = 1

    elif speedup <= 0 and result == 1:
        next_config = prev_config
        R = 0

    elif result == 0:
        next_config = prev_config 
        R = -99

    elif result == -1:
        next_config = prev_config 
        R = -99

    else:
        next_config = prev_config 
        R = -999

    return next_config, R, S_, q_table, S

def main():
    global ACTIONS
    global CONVERGENCE_CHECK

    if not os.path.exists(RESULTSDIR):
        os.makedirs(RESULTSDIR)
    elif os.path.exists(RESULTSDIR):
        os.system(f"rm -r {RESULTSDIR}/*.json")
    
    logging.basicConfig(filename='{}/qlearning-{}.log'.format(RESULTSDIR, time.strftime("%Y%m%d-%H%M%S")), level=logging.DEBUG)

    try:
        os.remove("log.dd")
    except OSError:
        pass

    original_conf_file = sys.argv[2]
    initial_config = []
    tmp_config = []
    state_config_map = {}

    run_orig_config(original_conf_file)
    original_score = utilities.get_dynamic_score()
    print(f"original_score: {original_score}")
    logging.info(f"original_score: {original_score}")

    S = 0
    episode = 0

    try:
        with open(original_conf_file, 'r') as original_json_file:
            original_json_data = json.load(original_json_file)
        
        output_filename = f"original_configuration.json"

        initial_config = gen_ini_state(original_json_data, output_filename, initial_config)

        ACTIONS = get_all_actions(initial_config)

        q_table = build_q_table(ACTIONS)

        tmp_config = utilities.convert_format(initial_config)

        for episode in range(30):            
            step = 0

            while len(ACTIONS) > 0:
                print(f"----------Episode: {episode} Steps: {step}------------")
                logging.info(f"----------Episode: {episode} Steps: {step}------------")

                selected_actions = []
                selected_actions = choose_action(S, q_table)
                
                next_config, R, S_, q_table, S = get_env_feedback(selected_actions, S, tmp_config, original_conf_file, original_score, state_config_map, q_table)
                tmp_config = next_config

                print(f"---------- State: {S} ------------")
                logging.info(f"---------- State: {S} ------------")
                
                if R == 999:
                    for i in range(len(selected_actions)):
                        q_predict = q_table.loc[S, selected_actions[i]]
                        q_target = R + GAMMA * q_table.loc[S_, :].max()
                        q_table.loc[S, selected_actions[i]] += ALPHA * (q_target - q_predict)

                        print(f"S: {S}")
                        print(f"selected_actions: {selected_actions[i]}")
                        print(f"S_: {S_}")
                        print(f"q_predict: {q_predict}")
                        print(f"q_target: {q_target}")
                        print(f"updated q value: {ALPHA * (q_target - q_predict)}")
                    
                    S = S_
                    step += 1

                    best_speedup = max(
                        [x.speedup for x in state_config_map.values() if x.result == 1],
                        default=None
                    )
                    best_speedups_state = max(
                        [x.state for x in state_config_map.values() if x.result == 1 and x.speedup == best_speedup],
                        default=None
                    )
                    best_speedup_config = [x.config for x in state_config_map.values() if x.result == 1 and x.speedup == best_speedup][0]

                    best_speedup_searched = [x.searched for x in state_config_map.values() if x.result == 1 and x.speedup == best_speedup][0]

                    print(f"best_speedup: State {best_speedups_state}, {best_speedup}")
                    logging.info(f"best_speedup: State {best_speedups_state}, {best_speedup}")

                    print(f"30% speedup is achieved.")
                    logging.info(f"30% speedup is achieved.")

                if int(FAIL_RESTAT_FLAG) == 1:
                    if R == -999:    
                        for i in range(len(selected_actions)):
                            q_predict = q_table.loc[S, selected_actions[i]]
                            q_target = R + GAMMA * q_table.loc[S_, :].max()
                            q_table.loc[S, selected_actions[i]] += ALPHA * (q_target - q_predict)

                        S = S_
                        step += 1

                        best_speedup = max(
                            [x.speedup for x in state_config_map.values() if x.result == 1],
                            default=None
                        )
                        best_speedups_state = max(
                            [x.state for x in state_config_map.values() if x.result == 1 and x.speedup == best_speedup],
                            default=None
                        )
                        print(f"best_speedup: State {best_speedups_state}, {best_speedup}")
                        logging.info(f"best_speedup: State {best_speedups_state}, {best_speedup}")

                        break
                                    
                for i in range(len(selected_actions)):
                    q_predict = q_table.loc[S, selected_actions[i]]
                    q_target = R + GAMMA * q_table.loc[S_, :].max()
                    q_table.loc[S, selected_actions[i]] += ALPHA * (q_target - q_predict)

                    print(f"S: {S}")
                    print(f"selected_actions: {selected_actions[i]}")
                    print(f"S_: {S_}")
                    print(f"q_predict: {q_predict}")
                    print(f"q_target: {q_target}")
                    print(f"updated q value: {ALPHA * (q_target - q_predict)}")
                
                S = S_
                step += 1

                best_speedup = max(
                    [x.speedup for x in state_config_map.values() if x.result == 1],
                    default=None
                )

                best_speedups_state = max(
                    [x.state for x in state_config_map.values() if x.result == 1 and x.speedup == best_speedup],
                    default=None
                )
                if best_speedup:
                    best_speedup_config = [x.config for x in state_config_map.values() if x.result == 1 and x.speedup == best_speedup][0]

                    best_speedup_searched = [x.searched for x in state_config_map.values() if x.result == 1 and x.speedup == best_speedup][0]
                elif not best_speedup:
                    print("No best configuration is found.")
                    logging.info("No best configuration is found.")

                print(f"best_speedup: State {best_speedups_state}, {best_speedup}")
                logging.info(f"best_speedup: State {best_speedups_state}, {best_speedup}")

            tmp_config = utilities.convert_format(initial_config)
            ACTIONS = get_all_actions(initial_config)

            if best_speedup:
                if not best_speedup_searched:
                    S = best_speedups_state

                    best_index = [key for key, value in state_config_map.items() if value.speedup == best_speedup and value.result == 1][0]
                    state_config_map[best_index] = state_config_map[best_index]._replace(searched=True)

                    tmp_config = utilities.convert_format(best_speedup_config)

                    print(f"Set the state to the best speedup state: {S}")
                    logging.info(f"Set the state to the best speedup state: {S}")
                else:
                    tried_best_speedups_state = [x.state for x in state_config_map.values() if x.result == 1 and x.speedup == best_speedup and x.searched == True][0]
                    print(f"Already tried the best speedup state: {tried_best_speedups_state}")
                    logging.info(f"Already tried the best speedup state: {tried_best_speedups_state}")
            else:
                print("No best speedup is found.")
                logging.info("No best speedup is found.")

            episode += 1
        
        q_table.to_csv(RESULTSDIR + "/q_table.csv")
        logging.info(f"q_table: {q_table}")

        print(f"FAIL_RESTAT_FLAG: {FAIL_RESTAT_FLAG} | greedy policy: {EPSILON} | learning rate: {ALPHA} | discount factor: {GAMMA}")
        logging.info(f"FAIL_RESTAT_FLAG: {FAIL_RESTAT_FLAG} | greedy policy: {EPSILON} | learning rate: {ALPHA} | discount factor: {GAMMA}")
        if best_speedup is None:
            print("0")
        else:
            final_best_filename = '{}/best_speedup_{}_{}.json'.format(RESULTSDIR, benchmark, best_speedups_state)
            utilities.transform_json(original_conf_file, final_best_filename, best_speedup_config)

            with open('{}/best_speedup_{}_{}.txt'.format(RESULTSDIR, benchmark, best_speedups_state), 'w') as f:
                print(best_speedup, file=f)
                print(f"{best_speedup}")

    except json.JSONDecodeError:
        print(f"Error: Unable to decode JSON error.")
        logging.info(f"Error: Unable to decode JSON error.")


if __name__ == "__main__":
  main()
