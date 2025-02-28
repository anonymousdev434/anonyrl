import sys, os, json, math, logging, time
from src import utilities as utilities

HIGHEST =-1
LOWEST = 0
TIME_ERROR = 0.05
benchmark = sys.argv[1] # in lower case

target_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), benchmark))
sys.path.append(target_dir)
import runner

TIME_OUT = int(sys.argv[4])
EPSILON = int(sys.argv[5])
CLASS = sys.argv[6]
RESULTSDIR = runner.setup(benchmark, TIME_OUT, EPSILON, CLASS)

glob_min_score = -1
glob_search_conf = -1
glob_min_idx = 0


def dd_search_config(change_set, type_set, switch_set, search_config, original_config, benchmark, div, original_score):
  #
  # partition change_set into deltas and delta inverses
  #
  global glob_min_score
  global glob_search_conf
  global glob_min_idx
  
  delta_change_set = []
  delta_type_set = []
  delta_switch_set = []
  delta_inv_change_set = []
  delta_inv_type_set = []
  delta_inv_switch_set = []
  div_size = int(math.ceil(float(len(change_set))/float(div)))
  for i in range(0, len(change_set), div_size):
    delta_change = []
    delta_type = []
    delta_switch = []
    delta_inv_change = []
    delta_inv_type = []
    delta_inv_switch = []
    for j in range(0, len(change_set)):
      if j >= i and j < i+div_size:
        delta_change.append(change_set[j])
        delta_type.append(type_set[j])
        delta_switch.append(switch_set[j])
      else:
        delta_inv_change.append(change_set[j])
        delta_inv_type.append(type_set[j])
        delta_inv_switch.append(switch_set[j])
    delta_change_set.append(delta_change)
    delta_type_set.append(delta_type)
    delta_switch_set.append(delta_switch)
    delta_inv_change_set.append(delta_inv_change)
    delta_inv_type_set.append(delta_inv_type)
    delta_inv_switch_set.append(delta_inv_switch)

  #
  # iterate through all delta and inverse delta set
  # record delta set that passes
  #
  pass_inx = -1
  inv_is_better = False
  min_score = -1

  for i in range(0, len(delta_change_set)):
    delta_change = delta_change_set[i]
    delta_type = delta_type_set[i]
    delta_switch = delta_switch_set[i]
    if len(delta_change) > 0:
      # always reset to lowest precision
      utilities.to_2nd_highest_precision(change_set, type_set, switch_set)
      # apply change for variables in delta
      utilities.to_highest_precision(delta_change, delta_type, switch_set)
      # record i if config passes
      if runner.run_config(search_config, original_config, benchmark) == 1 and utilities.get_dynamic_score() < original_score:
        score = utilities.get_dynamic_score()
        if score < glob_min_score or glob_min_score == -1:
          pass_inx = i
          inv_is_better = False
          # min_score = score
          glob_min_score = score
          glob_search_conf = search_config
          glob_min_idx = runner.search_counter - 1

    delta_inv_change = delta_inv_change_set[i]
    delta_inv_type = delta_inv_type_set[i]
    delta_inv_switch = delta_inv_switch_set[i]
    if len(delta_inv_change) > 0 and div > 2:
      # always reset to lowest precision
      utilities.to_2nd_highest_precision(change_set, type_set, switch_set)
      # apply change for variables in delta inverse
      utilities.to_highest_precision(delta_inv_change, delta_inv_type, delta_inv_switch)
      # record i if config passes
      if runner.run_config(search_config, original_config, benchmark) == 1 and utilities.get_dynamic_score() < original_score:
        score = utilities.get_dynamic_score()
        if score < glob_min_score or glob_min_score == -1:
          pass_inx = i
          inv_is_better = True
          # min_score = score
          glob_min_score = score
          glob_search_conf = search_config
          glob_min_idx = runner.search_counter - 1

  #
  # recursively search in pass delta or pass delta inverse
  # right now keep searching for the first pass delta or
  # pass delta inverse; later on we will integrate cost
  # model here
  #
  if pass_inx != -1:
    pass_change_set = delta_inv_change_set[pass_inx] if inv_is_better else delta_change_set[pass_inx]
    pass_type_set = delta_inv_type_set[pass_inx] if inv_is_better else delta_type_set[pass_inx]
    pass_switch_set = delta_inv_switch_set[pass_inx] if inv_is_better else delta_switch_set[pass_inx]
    # log the configuration if it is faster than original_score
    # to_2nd_highest_precision(change_set, type_set)
    # to_highest_precision(pass_change_set, pass_type_set)
    # run_config(search_config, original_config, bitcode)
    # modified_score = utilities.get_dynamic_score()
    # if modified_score <= original_score:
    # utilities.log_fast_config("fast_configs.cov", search_counter-1, modified_score)

    if len(pass_change_set) > 1:
      # always reset to lowest precision
      utilities.to_2nd_highest_precision(change_set, type_set, switch_set)
      dd_search_config(pass_change_set, pass_type_set, pass_switch_set, search_config, original_config, benchmark, 2, original_score)
    else:
      utilities.to_2nd_highest_precision(change_set, type_set, switch_set)
      utilities.to_highest_precision(pass_change_set, pass_type_set, pass_switch_set)
    return

  #
  # stop searching when division greater than change set size
  #
  if div >= len(change_set):
    utilities.to_highest_precision(change_set, type_set, switch_set)
    # log the configuration if it is faster than original_score
    # run_config(search_config, original_config, bitcode)
    # modified_score = utilities.get_dynamic_score()
    # if modified_score <= original_score:
    # utilities.log_fast_config("fast_configs.cov", search_counter-1, modified_score)
    return
  else:
    dd_search_config(change_set, type_set, switch_set, search_config, original_config, benchmark, 2*div, original_score)
    return


def search_config(change_set, type_set, switch_set, search_config, original_config, benchmark, original_score):
  # search from bottom up
  utilities.to_2nd_highest_precision(change_set, type_set, switch_set)
  if runner.run_config(search_config, original_config, benchmark) != 1 or utilities.get_dynamic_score() > original_score:
    dd_search_config(change_set, type_set, switch_set, search_config, original_config, benchmark, 2, original_score)
  # remove types and switches that cannot be changed
  for i in range(0, len(change_set)):
    if len(type_set[i]) > 0 and change_set[i]["type"] == type_set[i][HIGHEST]:
      del(type_set[i][:])
      if len(switch_set[i]) > 0:
        del(switch_set[i][:])

  # remove highest precision from each type vector
  for i in range(0, len(type_set)):
    type_vector = type_set[i]
    switch_vector = switch_set[i]
    if len(type_vector) > 0:
      type_vector.pop()
    if len(switch_vector) > 0:
      switch_vector.pop()
  return
  

def main():
  global benchmark
  search_conf_file = sys.argv[2]
  original_conf_file = sys.argv[3]

  if not os.path.exists(RESULTSDIR):
    os.makedirs(RESULTSDIR)

  logging.basicConfig(filename='{}/dd2-{}.log'.format(RESULTSDIR, time.strftime("%Y%m%d-%H%M%S")), level=logging.DEBUG)

  #
  # delete log file if exists
  #
  try:
    os.remove("log.dd")
  except OSError:
    pass

  #
  # parsing config files
  #
  search_conf = json.loads(open(search_conf_file, 'r').read())
  search_changes = search_conf
  original_conf = json.loads(open(original_conf_file, 'r').read())
  change_set = []
  type_set = []
  switch_set = []

  #
  # record the change set
  #
  for search_change in search_changes:
    type_vector = search_changes[search_change]["type"]
    if isinstance(type_vector, list):
      type_set.append(type_vector)
      change_set.append(search_changes[search_change])
    if "call" in search_change:
      switch_set.append(search_changes[search_change]["switch"])
    else:
      switch_set.append([])

  # search for valid configuration
  print("** Searching for valid configuration using delta-debugging algorithm")
  logging.info("** Searching for valid configuration using delta-debugging algorithm")


  # get original score
  utilities.to_highest_precision(change_set, type_set, switch_set)
  runner.run_orig_config(search_conf, original_conf, benchmark)
  original_score = utilities.get_dynamic_score() * (1 + TIME_ERROR) # allow 5% difference
  # original_score = utilities.get_dynamic_score()

  global original_runtime
  original_runtime = original_score

  # keep searching while the type set is not searched throughout
  while not utilities.is_empty(type_set):
    search_config(change_set, type_set, switch_set, search_conf, original_conf, benchmark, original_score)
  print(glob_search_conf, glob_min_score, glob_min_idx)
  # get the score of modified program
  if glob_min_score != -1:
    logging.info("Check dd2_valid_" + benchmark + ".json for the valid configuration file")
    print("Check dd2_valid_" + benchmark + ".json for the valid configuration file")
    json_string = json.dumps(glob_search_conf, indent=4)
    with open('{}/dd2_valid_{}_{}.json'.format(RESULTSDIR, benchmark, str(glob_min_idx)), 'w') as outfile:
      outfile.write(json_string)
    with open('{}/best_speedup_{}_{}.txt'.format(RESULTSDIR, benchmark, str(glob_min_idx)), 'w') as f:
      speedup = ((original_runtime - glob_min_score) / original_runtime) + 1
      print(speedup, file=f)
  else:
    logging.info("No valid and speedup configuration file!")
    print("No valid and speedup configuration file!")

  runner.df.to_csv(RESULTSDIR+'/df-configs.csv')


if __name__ == "__main__":
  main()
