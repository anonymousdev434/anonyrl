import json


include = {}
include["main.cpp"] = {}
include["main.cpp"]["function"] = {}
# add variables to exclude for each function
include["main.cpp"]["function"]["main"] = ["x", "b", "xexact", "times", "normr"]
include["main.cpp"]["function"]["HPCCG"] = ["b", "x", "times", "r", "p", "Ap", "rtrans", "alpha", "normr", "t4"]
include["main.cpp"]["function"]["generate_matrix"] = ["x", "b", "xexact", "curvalptr", "HPC_list_of_vals", "HPC_ptr_to_vals_in_row", "HPC_ptr_to_diags"]
include["main.cpp"]["function"]["HPC_sparsemv"] = ["x", "y", "cur_vals"]
include["main.cpp"]["function"]["compute_residual"] = ["v1", "v2", "residual"]
include["main.cpp"]["function"]["waxpby"] = ["w"]
include["main.cpp"]["function"]["ddot"] = ["x", "y", "result", "time_allreduce", "t4"]

# add global variables to include
#include["main.cpp"]["global"] = ["HPC_ptr_to_vals_in_row", "HPC_ptr_to_diags", "HPC_list_of_vals"]



with open('include.json', 'w', encoding='utf-8') as f:
    json.dump(include, f, ensure_ascii=False, indent=4)
    print("include.json is generated.")
