import os, json, logging, subprocess
import numpy as np
import pandas as pd
from src import utilities as utilities

search_counter = 0
EXE_COUNT = 10 

PROB_SIZE1 = "-i"
PROB_SIZE2 = "../tempscripts/kdd_bin"
PROB_SIZE3 = "-o"

original_runtime = 0
df = pd.DataFrame()

def setup(benchm, time_out, epsilon, class_name):
    global benchmark, TIME_OUT, EPSILON, RESULTSDIR, TO_RUN, benchfile, CLASS
    benchmark = benchm
    TIME_OUT = time_out
    EPSILON = epsilon
    CLASS = class_name
    
    RESULTSDIR = f"results-eps={EPSILON}"

    TO_RUN = "../tempscripts/kmeans"
    benchfile = "kmeans.cpp"

    return RESULTSDIR


def run_config(gen_index, config_index):
    global search_counter
    global original_runtime
    global df

    config_info_dict = {}

    # to record for each searched config
    config_info_dict["benchmark"] = benchmark

    config_filename = f"gen_{gen_index}_config_{config_index}.json"

    # Load the configuration from the file
    search_config = json.loads(open(config_filename, 'r').read())

    # Create a temporary JSON file
    json_string = json.dumps(search_config, indent=4)
    with open('config_temp.json', 'w') as outfile:
        outfile.write(json_string)

    print("-------- running gen {} config {} --------".format(gen_index, config_index))
    logging.info("-------- running gen {} config {} --------".format(gen_index, config_index))

    # Remove existing files
    os.system("rm ../tempscripts/{}".format(benchfile))
    os.system("python3 trans-type.py config_temp.json")

    # Copy the script to tempscripts if it doesn't exist
    if not os.path.exists("../tempscripts/{}".format(benchfile)):
        os.system("cp ../scripts/{} ../tempscripts/".format(benchfile))

    # # the thing you need to do before compiling
    # targetfile = os.path.join("../tempscripts", benchfile)
    # replacetxt = "../src/replacement.txt"
    # utilities.comment_before_make(targetfile, replacetxt)

    # delete previous log files and executable
    os.system("rm log.txt time.txt test_output")

    os.system(f"cd ../tempscripts; make clean; make")

    if os.path.exists(TO_RUN):
        print("Round 1:")
        process = subprocess.Popen([TO_RUN, PROB_SIZE1, PROB_SIZE2, PROB_SIZE3, "test_output"])
        try:
            process.wait(timeout=TIME_OUT)
        except subprocess.TimeoutExpired:
            print('Timed out - killing', process.pid)
            process.kill()
        os.system(f"../../utilities/quality -a accurate_output -t test_output -m MPP -e {EPSILON}")

    result = utilities.check_error()
    runtime = utilities.get_dynamic_score()
    print(f"runtime: {runtime}")
    logging.info(f"runtime: {runtime}")
    if result == 1:
        config_info_dict["label"] = "VALID"
        print("mv config_temp.json {}/{}.json".format(RESULTSDIR, "VALID_gen_" + str(gen_index) + "_config_" + str(config_index) + "_" + benchmark + "_" + str(search_counter)))
        os.system("mv config_temp.json {}/{}.json".format(RESULTSDIR, "VALID_gen_" + str(gen_index) + "_config_" + str(config_index) + "_" + benchmark + "_" + str(search_counter)))
        # run EXE_COUNT times in total to get average runtime
        avg_runtime = 0
        avg_runtime += runtime
        for i in range(EXE_COUNT - 1):
            if os.path.exists(TO_RUN):
                print("Round {}:".format(i+2))
                process = subprocess.Popen([TO_RUN, PROB_SIZE1, PROB_SIZE2, PROB_SIZE3, "test_output"])
                try:
                    process.wait(timeout=TIME_OUT)
                except subprocess.TimeoutExpired:
                    print('Timed out - killing', process.pid)
                    process.kill()
            runtime = utilities.get_dynamic_score()
            print(f"runtime: {runtime}")
            logging.info(f"runtime: {runtime}")
            avg_runtime += runtime
        avg_runtime = avg_runtime / EXE_COUNT
        with open('./time.txt', "w") as f:
            f.write(str(avg_runtime))
        runtime = avg_runtime
    elif result == 0:
        config_info_dict["label"] = "INVALID"
        print("mv config_temp.json {}/{}.json".format(RESULTSDIR, "INVALID_gen_" + str(gen_index) + "_config_" + str(config_index) + "_" + benchmark + "_" + str(search_counter)))
        os.system("mv config_temp.json {}/{}.json".format(RESULTSDIR, "INVALID_gen_" + str(gen_index) + "_config_" + str(config_index) + "_" + benchmark + "_" + str(search_counter)))
    elif result == -1:
        config_info_dict["label"] = "FAIL"
        print("mv config_temp.json {}/{}.json".format(RESULTSDIR, "FAIL_gen_" + str(gen_index) + "_config_" + str(config_index) + "_" + benchmark + "_" + str(search_counter)))
        os.system("mv config_temp.json {}/{}.json".format(RESULTSDIR, "FAIL_gen_" + str(gen_index) + "_config_" + str(config_index) + "_" + benchmark + "_" + str(search_counter)))

    time_to_log = utilities.get_dynamic_score()
    logging.info("runtime = {} s".format(time_to_log))
    print("Average runtime = {} s".format(runtime))

    config_info_dict["runtime"] = runtime
    if runtime >= original_runtime:
        config_info_dict["runtime_label"] = 0
    else:
        config_info_dict["runtime_label"] = 1

    if os.path.isfile("log.txt"):
        with open("log.txt") as f:
            firstline = f.readline().rstrip()
            err = f.readline().rstrip()
        config_info_dict["error"] = err
        config_info_dict["error_label"] = 1 if firstline == "true" else 0
    else:
        config_info_dict["error"] = np.nan
        config_info_dict["error_label"] = 0

    df_item = pd.DataFrame(config_info_dict, index=[0])
    df = pd.concat([df, df_item], ignore_index=True)
    df.to_csv(RESULTSDIR+'/df-configs.csv')

    search_counter = search_counter + 1
    return result, runtime


def run_orig_config(original_config):
    global search_counter
    global original_runtime
    global df

    config_info_dict = {}

    # to record for each searched config
    config_info_dict["benchmark"] = benchmark

    with open(original_config, 'r') as original_json_file:
        original_config_data = json.load(original_json_file)

    json_string = json.dumps(original_config_data, indent=4)

    with open('config_temp.json', 'w') as outfile:
        outfile.write(json_string)

    print("-------- running original config {} --------".format(search_counter))
    logging.info("-------- running original config {} --------".format(search_counter))

    os.system("rm ../tempscripts/{}".format(benchfile))
    os.system("python3 trans-type.py config_temp.json")

    if not os.path.exists("../tempscripts/{}".format(benchfile)):
        os.system("cp ../scripts/{} ../tempscripts/".format(benchfile))

    # # the thing you need to do before compiling
    # targetfile = os.path.join("../tempscripts", benchfile)
    # replacetxt = "../src/replacement.txt"
    # utilities.comment_before_make(targetfile, replacetxt)

    # delete previous log files and executable
    os.system("rm log.txt time.txt accurate_output")

    # step 3: recompile modified cg.c into executable
    os.system("cd ../tempscripts; make clean; make")

    if os.path.exists(TO_RUN):
        print("Round 1:")
        process = subprocess.Popen([TO_RUN, PROB_SIZE1, PROB_SIZE2, PROB_SIZE3, "accurate_output"])
        try:
            process.wait(timeout=TIME_OUT)
        except subprocess.TimeoutExpired:
            print('Timed out - killing', process.pid)
            process.kill()
        os.system(f"../../utilities/quality -a accurate_output -t accurate_output -m MPP -e {EPSILON}")

    result = utilities.check_error()
    runtime = utilities.get_dynamic_score()
    print(f"runtime: {runtime}")
    logging.info(f"runtime: {runtime}")

    if result == 1:
        config_info_dict["label"] = "VALID"
        print("mv config_temp.json {}/{}.json".format(RESULTSDIR, "VALID_orig_config_" + benchmark + "_" + str(search_counter)))
        os.system("mv config_temp.json {}/{}.json".format(RESULTSDIR, "VALID_orig_config_" + benchmark + "_" + str(search_counter)))
        # run EXE_COUNT times in total to get average runtime
        avg_runtime = 0
        avg_runtime += runtime
        for i in range(EXE_COUNT - 1):
            if os.path.exists(TO_RUN):
                print("Round {}:".format(i+2))
                process = subprocess.Popen([TO_RUN, PROB_SIZE1, PROB_SIZE2, PROB_SIZE3, "accurate_output"])
                try:
                    process.wait(timeout=TIME_OUT)
                except subprocess.TimeoutExpired:
                    print('Timed out - killing', process.pid)
                    process.kill()
            runtime = utilities.get_dynamic_score()
            print(f"runtime: {runtime}")
            logging.info(f"runtime: {runtime}")
            avg_runtime += runtime
        avg_runtime = avg_runtime / EXE_COUNT
        with open('./time.txt', "w") as f:
            f.write(str(avg_runtime))
        runtime = avg_runtime
    elif result == 0:
        config_info_dict["label"] = "INVALID"
        print("mv config_temp.json {}/{}.json".format(RESULTSDIR, "INVALID_orig_config_" + benchmark + "_" + str(search_counter)))
        os.system("mv config_temp.json {}/{}.json".format(RESULTSDIR, "INVALID_orig_config_" + benchmark + "_" + str(search_counter)))
    elif result == -1:
        config_info_dict["label"] = "FAIL"
        print("mv config_temp.json {}/{}.json".format(RESULTSDIR, "FAIL_orig_config_" + benchmark + "_" + str(search_counter)))
        os.system("mv config_temp.json {}/{}.json".format(RESULTSDIR, "FAIL_orig_config_" + benchmark + "_" + str(search_counter)))

    time_to_log = utilities.get_dynamic_score()
    logging.info("Average runtime = {} s".format(time_to_log))
    print("Average runtime = {} s".format(runtime))

    config_info_dict["runtime"] = runtime
    if runtime >= original_runtime:
        config_info_dict["runtime_label"] = 0
    else:
        config_info_dict["runtime_label"] = 1

    if os.path.isfile("log.txt"):
        with open("log.txt") as f:
            firstline = f.readline().rstrip()
            err = f.readline().rstrip()

        config_info_dict["error"] = err
        config_info_dict["error_label"] = 1 if firstline == "true" else 0
    else:
        config_info_dict["error"] = np.nan
        config_info_dict["error_label"] = 0

    df_item = pd.DataFrame(config_info_dict, index=[0])
    df = pd.concat([df, df_item], ignore_index=True)
    df.to_csv(RESULTSDIR+'/df-configs.csv')

    search_counter = search_counter + 1
    return result

