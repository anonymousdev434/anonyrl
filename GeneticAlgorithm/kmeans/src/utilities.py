import random, json, logging, os
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
#random.seed(42)

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


#
# modify change set so that each variable
# maps to its highest type
#
def to_highest_precision(change_set, type_set, switch_set):
  for i in range(0, len(change_set)):
    c = change_set[i]
    t = type_set[i]
    if len(t) > 0:
      c["type"] = t[HIGHEST]
    if len(switch_set) > 0:
      s = switch_set[i]
      if len(s) > 0:
        c["switch"] = s[HIGHEST]


#
# modify change set so that each variable
# maps to its 2nd highest type
#
def to_2nd_highest_precision(change_set, type_set, switch_set):
  for i in range(0, len(change_set)):
    c = change_set[i]
    t = type_set[i]
    if len(t) > 1:
      c["type"] = t[LOWEST]
    if len(switch_set) > 0:
      s = switch_set[i]
      if len(s) > 1:
        c["switch"] = s[LOWEST]


# combine.py

def isNumber (value):
    return True if type(value) in [int, float] else str(value).replace('.','',1).isdigit()


def combineCSV(outdir, edgeout, nodeout):
  # edges
  edge_list = []
  edge_list.append(":START_ID,:END_ID,:TYPE,:VARIABLE\n")
  for csvfile in os.listdir(outdir):
              parse = csvfile.replace(".csv", "").split("_")
              if parse[0] == "edges" and parse[-1] == "data":
                  data_path = os.path.join(outdir, csvfile)
                  with open(data_path) as f1:
                      for line in f1:
                          if isNumber(line.split(',')[0]) and isNumber(line.split(',')[1]):
                              if len(line.split(',')) == 4:
                                  edge_list.append(line)
                              elif len(line.split(',')) == 3:
                                  line = line.replace('\n', '') + ',\n'
                                  edge_list.append(line)     
              
  with open(edgeout, "w") as f2:
                      for line in edge_list:
                          f2.write(line)

  # nodes
  node_list = []
  node_list.append(":ID,:LABEL,:DATATYPE,:NAME\n")
  for csvfile in os.listdir(outdir):
              parse = csvfile.replace(".csv", "").split("_")
              data_path = os.path.join(outdir, csvfile)

              if parse[0] == "nodes" and parse[-1] == "data" and parse[1] == "CALL":
                  with open(data_path) as f1:
                      for line in f1:
                          if isNumber(line.split(',')[0]):
                              templine = line.split(',')[0] + ',' + line.split(',')[1] + ',' + ',' + line.split(',')[-4] + '\n'
                              node_list.append(templine)
              elif parse[0] == "nodes" and parse[-1] == "data" and parse[1] == "IDENTIFIER":
                  with open(data_path) as f1:
                      for line in f1:
                          if isNumber(line.split(',')[0]):
                              templine = line.split(',')[0] + ',' + line.split(',')[1] + ',' + line.split(',')[-1].replace('\n', '') + ',' + line.split(',')[-3] + '\n'
                              node_list.append(templine)
              elif parse[0] == "nodes" and parse[-1] == "data" and parse[1] == "LITERAL":
                  with open(data_path) as f1:
                      for line in f1:
                          templine = line.split(',')[0] + ',' + line.split(',')[1] + ',' + line.split(',')[-1].replace('\n', '') + ',' + line.split(',')[4] + '\n'
                          node_list.append(templine)
              elif parse[0] == "nodes" and parse[-1] == "data" and parse[1] == "LOCAL":
                  with open(data_path) as f1:
                      for line in f1:
                          templine = line.split(',')[0] + ',' + line.split(',')[1] + ',' + line.split(',')[-1].replace('\n', '') + ',' + line.split(',')[-3] + '\n'
                          node_list.append(templine)
              elif parse[0] == "nodes" and parse[-1] == "data" and parse[1] == "METHOD" and len(parse) == 3:
                  with open(data_path) as f1:
                      for line in f1:
                          if isNumber(line.split(',')[0]):
                              templine = line.split(',')[0] + ',' + line.split(',')[1] + ','  + ',' + line.split(',')[-3] + '\n'
                              node_list.append(templine)
              elif parse[0] == "nodes" and parse[-1] == "data" and parse[1] == "METHOD" and parse[-2] == "IN":
                  with open(data_path) as f1:
                      for line in f1:
                          templine = line.split(',')[0] + ',' + line.split(',')[1] + ',' + line.split(',')[-1].replace('\n', '') + ',' + line.split(',')[-3] + '\n'
                          node_list.append(templine)
              elif parse[0] == "nodes" and parse[-1] == "data" and parse[1] == "METHOD" and parse[-2] == "OUT":
                  with open(data_path) as f1:
                      for line in f1:
                          templine = line.split(',')[0] + ',' + line.split(',')[1] + ',' + line.split(',')[-1].replace('\n', '') + ',' + line.split(',')[-3] + '\n'
                          node_list.append(templine)
              elif parse[0] == "nodes" and parse[-1] == "data" and parse[1] == "METHOD" and parse[-2] == "RETURN":
                  with open(data_path) as f1:
                      for line in f1:
                          templine = line.split(',')[0] + ',' + line.split(',')[1] + ',' + line.split(',')[-1].replace('\n', '') + ',' + '\n'
                          node_list.append(templine)
              elif parse[0] == "nodes" and parse[-1] == "data" and parse[-2] == "TYPE":
                  with open(data_path) as f1:
                      for line in f1:
                          templine = line.split(',')[0] + ',' + line.split(',')[1] + ',' + line.split(',')[-1].replace('\n', '') + ',' + '\n'
                          node_list.append(templine)
              elif parse[0] == "nodes" and parse[-1] == "data" and parse[-2] == "DECL":
                  with open(data_path) as f1:
                      for line in f1:
                          if isNumber(line.split(',')[0]):
                              templine = line.split(',')[0] + ',' + line.split(',')[1] + ',' + line.split(',')[-2] + ',' + '\n'
                              node_list.append(templine)
              elif parse[0] == "nodes" and parse[-1] == "data" :
                  with open(data_path) as f1:
                      for line in f1:
                          if isNumber(line.split(',')[0]):
                              templine = line.split(',')[0] + ',' + line.split(',')[1] + ',' + ',' + '\n'
                              node_list.append(templine)

  with open(nodeout, "w") as f2:
                      for line in node_list:
                          f2.write(line)


# add_edges.py
nodedf = 0
tree = {}
upcasting = {':START_ID': [],
        ':END_ID': [],
        ':TYPE': [],
        ':VARIABLE': []}
downcasting = {':START_ID': [],
        ':END_ID': [],
        ':TYPE': [],
        ':VARIABLE': []}
dependence = {':START_ID': [],
        ':END_ID': [],
        ':TYPE': [],
        ':VARIABLE': []}

def createTreeFromEdges(edges):
    tree = {}
    for v1, v2 in edges:
        tree.setdefault(v1, []).append(v2)
    return tree


def setdefault(self, key, default=None):
    if key not in self:
        self[key] = default
    return self[key]


def postTraverse(node):
    if node:
        # if node is not leaf
        if node in tree.keys():
            tn = tree[node]
            for child in tree[node]:
                postTraverse(child)

        if (nodedf[':ID'] == node).any():
            row = nodedf.loc[nodedf[':ID'] == node]
            name = str(row[':NAME'].values[0])
            label = str(row[':LABEL'].values[0])
            index = row.index[0]
            if 'CALL' in label and ('exp' in name or 'log' in name or 'sin' in name
                                    or 'tan' in name or 'cos' in name or 'sqrt' in name
                                    or 'abs' in name or 'pow' in name or 'floor' in name
                                    or 'ceil' in name or 'mod' in name):
                nodedf.at[index, ':DATATYPE'] = 'double'
                # print(node, name)
                # print(tree[node])
                child = tree[node][0]
                if (nodedf[':ID'] == child).any():
                    child_type = str(nodedf.loc[nodedf[':ID'] == child][':DATATYPE'].values[0])
                    # print(child_type)
                    if 'float' in child_type:
                        upcasting[':START_ID'].append(child)
                        upcasting[':END_ID'].append(node)
                        upcasting[':TYPE'].append('UP_CASTING')
                        upcasting[':VARIABLE'].append(np.NaN)
            if '<operator>' in name:
                # print(node, name)
                # print(tree[node])
                if len(tree[node]) == 1:
                    if 'plus' in name or 'minus' in name:
                        child = tree[node][0]
                        if not (nodedf[':ID'] == child).any():
                            nodedf.at[index, ':DATATYPE'] = 'double'
                        else:
                            child_label = str(nodedf.loc[nodedf[':ID'] == child][':LABEL'].values[0])
                            if 'LITERAL' in child_label:
                                child_type = str(nodedf.loc[nodedf[':ID'] == child][':DATATYPE'].values[0])
                                # print(child_type)
                                if 'float' in child_type:
                                    nodedf.at[index, ':DATATYPE'] = 'float'
                                elif 'double' in child_type:
                                    nodedf.at[index, ':DATATYPE'] = 'double'

                elif len(tree[node]) == 2:
                    left_child = tree[node][0]
                    right_child = tree[node][1]
                    if not (nodedf[':ID'] == left_child).any() or not (nodedf[':ID'] == right_child).any():
                        return
                    left_child_label = str(nodedf.loc[nodedf[':ID'] == left_child][':LABEL'].values[0])
                    right_child_label = str(nodedf.loc[nodedf[':ID'] == right_child][':LABEL'].values[0])

                    if 'indirectIndexAccess' in name:
                        if 'IDENTIFIER' in left_child_label:  # and 'LITERAL' in right_child_label:
                            left_child_type = str(nodedf.loc[nodedf[':ID'] == left_child][':DATATYPE'].values[0])
                            if 'float' in left_child_type:
                                nodedf.at[index, ':DATATYPE'] = 'float'
                            elif 'double' in left_child_type:
                                nodedf.at[index, ':DATATYPE'] = 'double'
                        elif 'IDENTIFIER' in right_child_label:  # and 'LITERAL' in left_child_label:
                            right_child_type = str(nodedf.loc[nodedf[':ID'] == right_child][':DATATYPE'].values[0])
                            if 'float' in right_child_type:
                                nodedf.at[index, ':DATATYPE'] = 'float'
                            elif 'double' in right_child_type:
                                nodedf.at[index, ':DATATYPE'] = 'double'
                    else:
                        if ('IDENTIFIER' in left_child_label or 'CALL' in left_child_label or 'LITERAL' in left_child_label) \
                                and ('IDENTIFIER' in right_child_label or 'CALL' in right_child_label or 'LITERAL' in right_child_label):
                            left_child_type = str(nodedf.loc[nodedf[':ID'] == left_child][':DATATYPE'].values[0])
                            right_child_type = str(nodedf.loc[nodedf[':ID'] == right_child][':DATATYPE'].values[0])
                            # print(left_child_type, right_child_type)

                            if 'float' in left_child_type and 'float' in right_child_type:
                                nodedf.at[index, ':DATATYPE'] = 'float'
                            elif 'double' in left_child_type and 'double' in right_child_type:
                                nodedf.at[index, ':DATATYPE'] = 'double'
                            elif 'float' in left_child_type and 'double' in right_child_type:
                                if 'assignment' in name:
                                    # newedge = [right_child, node]
                                    # downcasting.append(newedge)
                                    downcasting[':START_ID'].append(right_child)
                                    downcasting[':END_ID'].append(node)
                                    downcasting[':TYPE'].append('DOWN_CASTING')
                                    downcasting[':VARIABLE'].append(np.NaN)
                                    nodedf.at[index, ':DATATYPE'] = 'float'
                                else:
                                    # newedge = [left_child, node]
                                    # upcasting.append(newedge)
                                    upcasting[':START_ID'].append(left_child)
                                    upcasting[':END_ID'].append(node)
                                    upcasting[':TYPE'].append('UP_CASTING')
                                    upcasting[':VARIABLE'].append(np.NaN)
                                    nodedf.at[index, ':DATATYPE'] = 'double'
                            elif 'double' in left_child_type and 'float' in right_child_type:
                                # newedge = [right_child, node]
                                # upcasting.append(newedge)
                                upcasting[':START_ID'].append(right_child)
                                upcasting[':END_ID'].append(node)
                                upcasting[':TYPE'].append('UP_CASTING')
                                upcasting[':VARIABLE'].append(np.NaN)
                                nodedf.at[index, ':DATATYPE'] = 'double'
            if 'assignment' in name:
                if len(tree[node]) == 2:
                    left_child = tree[node][0]
                    right_child = tree[node][1]
                    if not (nodedf[':ID'] == left_child).any() or not (nodedf[':ID'] == right_child).any():
                        return
                    left_child_label = str(nodedf.loc[nodedf[':ID'] == left_child][':LABEL'].values[0])
                    right_child_label = str(nodedf.loc[nodedf[':ID'] == right_child][':LABEL'].values[0])

                    def _get_leaf_nodes(node, leafs):
                        if node:
                            if node not in tree.keys():
                                leafs.append(node)
                            else:
                                for child in tree[node]:
                                    _get_leaf_nodes(child, leafs)

                    if 'LITERAL' not in right_child_label:
                        left_leafs = []
                        _get_leaf_nodes(left_child, left_leafs)
                        point_to_node = False
                        if len(left_leafs) == 1 and 'IDENTIFIER' in left_child_label:
                            point_to_node = left_child
                        elif len(left_leafs) == 2:
                            leaf1 = left_leafs[0]
                            leaf2 = left_leafs[1]
                            leaf1_label = str(nodedf.loc[nodedf[':ID'] == leaf1][':LABEL'].values[0])
                            leaf2_label = str(nodedf.loc[nodedf[':ID'] == leaf2][':LABEL'].values[0])
                            if 'IDENTIFIER' in leaf1_label:
                                point_to_node = leaf1
                            elif 'IDENTIFIER' in leaf2_label:
                                point_to_node = leaf2

                        right_leafs = []
                        _get_leaf_nodes(right_child, right_leafs)
                        for leaf in right_leafs:
                            if nodedf.loc[nodedf[':ID'] == leaf][':LABEL'].values.size > 0 and nodedf.loc[nodedf[':ID'] == leaf][':DATATYPE'].values.size > 0:
                                leaf_label = str(nodedf.loc[nodedf[':ID'] == leaf][':LABEL'].values[0])
                                leaf_type = str(nodedf.loc[nodedf[':ID'] == leaf][':DATATYPE'].values[0])
                                if point_to_node and 'IDENTIFIER' in leaf_label and ('float' in leaf_type or 'double' in leaf_type):
                                    dependence[':START_ID'].append(leaf)
                                    dependence[':END_ID'].append(point_to_node)
                                    dependence[':TYPE'].append('DEPENDENCE')
                                    dependence[':VARIABLE'].append(np.NaN)


def addEdges(edge_file, node_file, root):
  global nodedf

  nodedf = pd.read_csv(node_file)
  edgedf = pd.read_csv(edge_file)
  edge_list = edgedf[edgedf[':TYPE'] == 'AST']
  edge_list = edge_list[[":START_ID", ":END_ID"]].values.tolist()

  global tree
  global upcasting
  global downcasting
  global dependence
  
  tree = createTreeFromEdges(edge_list)

  upcasting = {':START_ID': [],
            ':END_ID': [],
            ':TYPE': [],
            ':VARIABLE': []}
  downcasting = {':START_ID': [],
            ':END_ID': [],
            ':TYPE': [],
            ':VARIABLE': []}
  dependence = {':START_ID': [],
                    ':END_ID': [],
                    ':TYPE': [],
                    ':VARIABLE': []}
  
  row = nodedf.loc[nodedf[':ID'] == root]
  if not row.empty:
    name = str(row[':NAME'].values[0])
    if 'global' in name:
      postTraverse(root)
      upc_df = pd.DataFrame(upcasting)
      dnc_df = pd.DataFrame(downcasting)
      dpd_df = pd.DataFrame(dependence)
      edgedf = pd.concat([edgedf, upc_df, dnc_df, dpd_df], ignore_index = True, axis = 0)
  nodedf.to_csv(node_file, index=False)
  edgedf.to_csv(edge_file, index=False)


# denoise_csv.py

def denoiseCSV(edge_file, node_file):
    nodedf = pd.read_csv(node_file)
    edgedf = pd.read_csv(edge_file)
    rslt_edgedf = edgedf[(edgedf[':TYPE'] == 'AST') | (edgedf[':TYPE'] == 'CONDITION') | (edgedf[':TYPE'] == 'CFG')
                    | (edgedf[':TYPE'] == 'CDG') | (edgedf[':TYPE'] == 'REACHING_DEF') 
                    | (edgedf[':TYPE'] == 'UP_CASTING') | (edgedf[':TYPE'] == 'DOWN_CASTING')
                    | (edgedf[':TYPE'] == 'DEPENDENCE')
                    | (edgedf[':TYPE'] == 'CALL')]

    todrop_idx = nodedf[(nodedf[':LABEL'] == 'METHOD_PARAMETER_IN')
                        | (nodedf[':LABEL'] == 'METHOD_PARAMETER_OUT')
                        | (nodedf[':LABEL'] == 'METHOD_RETURN')
                        | (nodedf[':LABEL'] == 'METHOD')
                        | (nodedf[':LABEL'] == 'NAMESPACE')
                        | (nodedf[':LABEL'] == 'NAMESPACE_BLOCK')
                        | (nodedf[':LABEL'] == 'MEMBER')
                        | (nodedf[':LABEL'] == 'TYPE')
                        | (nodedf[':LABEL'] == 'TYPE_ARGUMENT')
                        | (nodedf[':LABEL'] == 'TYPE_DECL')
                        | (nodedf[':LABEL'] == 'TYPE_PARAMETER')
                        | (nodedf[':LABEL'] == 'META_DATA')
                        | (nodedf[':LABEL'] == 'FILE')
                        | (nodedf[':LABEL'] == 'BINDING')
                        ].index
    todrop = nodedf.loc[todrop_idx]
    a = todrop[':ID'].values

    index = rslt_edgedf.index
    for i in index:
        oldID_start = rslt_edgedf.at[i, ':START_ID']
        oldID_end = rslt_edgedf.at[i, ':END_ID']
        if oldID_start in a or oldID_end in a:
            rslt_edgedf = rslt_edgedf.drop(i)

    edge_index = np.ravel(rslt_edgedf[[":START_ID", ":END_ID"]].values.tolist())
    connected_nodes = set(edge_index)
    rslt_nodedf = nodedf.loc[nodedf[':ID'].isin(connected_nodes)]
    rslt_nodedf = rslt_nodedf.sort_values(by=[':ID'])

    nodemap = {}
    idx = 0
    for node in connected_nodes:
        nodemap[node] = idx
        idx += 1

    for i in rslt_nodedf.index:
        oldID = rslt_nodedf.at[i, ':ID']
        rslt_nodedf.at[i, ':ID'] = nodemap[oldID]
    for i in rslt_edgedf.index:
        oldID_start = rslt_edgedf.at[i, ':START_ID']
        oldID_end = rslt_edgedf.at[i, ':END_ID']
        rslt_edgedf.at[i, ':START_ID'] = nodemap[oldID_start]
        rslt_edgedf.at[i, ':END_ID'] = nodemap[oldID_end]
    
    
    rslt_nodedf.to_csv(node_file, index=False)
    rslt_edgedf.to_csv(edge_file, index=False)



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
          if number not in range(146+17, 612+17):
              fp.write(line)


def comment_before_make(targetfile, replacetxt):
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