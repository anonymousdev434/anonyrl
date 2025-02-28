import random, json, logging, os
import numpy as np



seg_time = 9999


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
    
  return zero_one_vec


def get_dynamic_score():
  score = seg_time
  if os.path.isfile("time.txt"):
    with open("time.txt") as scorefile:
      temp = scorefile.readline().strip()
      if temp:
        score = temp
  return float(score)


def check_error():
  if os.path.isfile("log.txt"):
    with open("log.txt") as f:
      firstline = f.readline().rstrip()
      print("log.txt firstline within err threshold: {}".format(firstline))
      logging.info("within err threshold: {}".format(firstline))
            
     # FOR CG:
      zeta = f.readline().rstrip()
      err = f.readline().rstrip()
      logging.info("within err threshold: {}, zeta = {}, error = {}".format(firstline, zeta, err))

     # FOR EP:
      # sx = f.readline().rstrip()
      # sx_err = f.readline().rstrip()
      # sy = f.readline().rstrip()
      # sy_err = f.readline().rstrip()
      # logging.info("within err threshold: {}, sx = {}, sx_err = {}, sy = {}, sy_err = {}".format(firstline, sx, sx_err, sy, sy_err))

     # For BT:
      # logging.info("within err threshold: {}".format(firstline))


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


def replace_before_make(targetfile, replacetxt):
  with open(replacetxt, 'r') as fp:
    values = fp.readlines()

  with open(targetfile, 'r') as fp:
      # read an store all lines into list
      lines = fp.readlines()


  values.extend(lines)
  # Write file
  with open(targetfile, 'w') as fp:
      # iterate each line
      for number, line in enumerate(values):
          fp.write(line)
          #if number not in range(3+17, 469+17):
              #fp.write(line)


# candidate type
def choose_random_type():
    #types = ["double", "float", "long double"]
    types = ["double", "float"]
    return random.choice(types)

def compare_results(original_results, mutated_results, label_original, label_modified):
    for i, (original_result, modified_result) in enumerate(zip(original_results, mutated_results), start=1):
        print(f"Comparison between {label_original} and {label_modified} for Offspring_{i}:")

        for j, (original_gene, modified_gene) in enumerate(zip(original_result, modified_result), start=1):
            if original_gene[2] != modified_gene[2]:
                print(f"  Offspring_{i} - Gene {j} changed by Mutation:")
                print(f"    {label_original}: {original_gene[1]}: {original_gene[2]}")
                print(f"    {label_modified}: {modified_gene[1]}: {modified_gene[2]}\n")

# convert format of population to array
def convert_format(pop):
    formatted_pop = []
    for entry in pop:
        formatted_entry = entry.copy()
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

        if key.startswith("call"):
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

