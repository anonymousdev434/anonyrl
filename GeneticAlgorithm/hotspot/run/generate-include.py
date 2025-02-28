import json


include = {}
include["hotspot_openmp.cpp"] = {}
include["hotspot_openmp.cpp"]["function"] = {}
# add variables to exclude for each function
include["hotspot_openmp.cpp"]["function"]["single_iteration"] = ["result", "temp", "power", "r", "t"]
include["hotspot_openmp.cpp"]["function"]["compute_tran_temp"] = ["result", "temp", "power",  "r", "t", "tmp"]
include["hotspot_openmp.cpp"]["function"]["writeoutput"] = ["vect"]
include["hotspot_openmp.cpp"]["function"]["main"] = ["result", "temp", "power"]

# add global variables to include
include["hotspot_openmp.cpp"]["global"] = ["t_chip", "chip_height", "chip_width", "amb_temp"]


with open('include.json', 'w', encoding='utf-8') as f:
    json.dump(include, f, ensure_ascii=False, indent=4)
    print("include.json is generated.")
