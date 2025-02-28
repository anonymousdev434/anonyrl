import json


include = {}
include["main.cpp"] = {}
include["main.cpp"]["function"] = {}
# add variables to exclude for each function
include["main.cpp"]["function"]["main"] = []
include["main.cpp"]["function"]["HPCCG"] = []
include["main.cpp"]["function"]["generate_matrix"] = []
include["main.cpp"]["function"]["HPC_sparsemv"] = []
include["main.cpp"]["function"]["compute_residual"] = []
include["main.cpp"]["function"]["waxpby"] = []
include["main.cpp"]["function"]["ddot"] = []

# add global variables to include
include["main.cpp"]["global"] = ["HPC_ptr_to_vals_in_row", "HPC_ptr_to_diags", "HPC_list_of_vals"]



with open('include.json', 'w', encoding='utf-8') as f:
    json.dump(include, f, ensure_ascii=False, indent=4)
    print("include.json is generated.")
