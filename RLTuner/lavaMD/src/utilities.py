import logging
import os
import random, json
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))



seg_time = 9999
HIGHEST =-1
LOWEST = 0


def get_digit(str_name):
  digit = ""
  for s in str_name:
    if s.isdigit():
      digit += s
  return int(digit)

def parse_json(search_config):
  search_config_len = len(search_config)
  zero_one_vec = [-1] * search_config_len
  for item in search_config:
    idx = get_digit(item[0]) - 1
    zero_one_vec[idx] = 1 if "double" in item[2] else 0
    # zero_one_vec[idx] = 1 if "double" in item[3] else 0

  return zero_one_vec


def get_dynamic_score():
  score = seg_time
  if os.path.isfile("time.txt"):
    with open("time.txt") as scorefile:
      score = scorefile.readline().strip()
  return float(score)


def check_error():
  if os.path.isfile("log.txt"):
    with open("log.txt") as f:
      firstline = f.readline().rstrip()
    #   print(firstline)
    #   logging.info("firstline: {}".format(firstline))

     # FOR CG:
      err = f.readline().rstrip()
      logging.info("within err threshold: {}, error = {}".format(firstline, err))

     # FOR EP:
     #  sx = f.readline().rstrip()
     #  sx_err = f.readline().rstrip()
     #  sy = f.readline().rstrip()
     #  sy_err = f.readline().rstrip()
     #  logging.info("within err threshold: {}, sx = {}, sx_err = {}, sy = {}, sy_err = {}".format(firstline, sx, sx_err, sy, sy_err))

     # For BT:
    #   logging.info("within err threshold: {}, MaxAbsDiff = {}".format(firstline, MaxAbsDiff))


    if firstline == "true":
      return 1
    else:
      return 0
  else:
#     segmentation fault
    logging.info("segmentation fault")
    return -1


def is_empty(type_set):
  for t in type_set:
    if len(t) > 1:
      return False
  return True

# arbitrary seed
# random.seed(42)

# candidate type
def choose_random_type():
    #types = ["double", "float", "long double"]
    types = ["double", "float"]
    return random.choice(types)

# convert format of population to array
def convert_format(pop):
    formatted_pop = []
    for entry in pop:
        formatted_entry = entry.copy()
        # formatted_entry[2] = entry[2]

        # if isinstance(formatted_entry[3], list):
        #     formatted_entry[3] = formatted_entry[3][0]
        formatted_entry[1] = entry[1]

        if isinstance(formatted_entry[2], list):
            formatted_entry[2] = formatted_entry[2][0]
        formatted_pop.append(formatted_entry)
    return formatted_pop

# transform array to json file for execution
def transform_json(original_conf_file, output_filename, mutated_offspring):
    json_form = {}

    with open(original_conf_file, 'r') as original_json_file:
        original_json_data = json.load(original_json_file)

    for mutation in mutated_offspring:
        key = mutation[0]
        name = mutation[1]
        new_type = mutation[2]
        # name = mutation[2]
        # new_type = mutation[3]

        if key.startswith("call") and name in ["sqrt", "log", "sin", "cos", "exp"] and "float" in new_type:
            if key in original_json_data:
                json_form[key] = {
                    "file": original_json_data[key].get("file", ""),
                    "function": original_json_data[key].get("function", ""),
                    "lines": original_json_data[key].get("lines", []),
                    "location": original_json_data[key].get("location", ""),
                    "name": name,
                    "switch": name + "f",
                    "type": [new_type, new_type],
                }
        elif key.startswith("call"):
            if key in original_json_data:
                json_form[key] = {
                    "file": original_json_data[key].get("file", ""),
                    "function": original_json_data[key].get("function", ""),
                    "lines": original_json_data[key].get("lines", []),
                    "location": original_json_data[key].get("location", ""),
                    "name": name,
                    "switch": name,
                    "type": [new_type, new_type],
                }
        elif key.startswith("global"):
            if key in original_json_data:
                json_form[key] = {
                    "file": original_json_data[key].get("file", ""),
                    "lines": original_json_data[key].get("lines", []),
                    "location": original_json_data[key].get("location", ""),
                    "name": name,
                    "type": new_type,
                }
        else:
            if key in original_json_data:
                json_form[key] = {
                    "file": original_json_data[key].get("file", ""),
                    "function": original_json_data[key].get("function", ""),
                    "lines": original_json_data[key].get("lines", []),
                    "location": original_json_data[key].get("location", ""),
                    "name": name,
                    "type": new_type,
                }

    with open(output_filename, 'w') as outfile:
        json.dump(json_form, outfile, indent=4)
