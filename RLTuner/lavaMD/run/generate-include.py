import json


include = {}
include["main.cpp"] = {}
include["main.cpp"]["function"] = {}
# add variables to exclude for each function
include["main.cpp"]["function"]["kernel_cpu"] = []
include["main.cpp"]["function"]["main"] = []



# add global variables to include
include["main.cpp"]["global"] = ["par_alpha"]


with open('include.json', 'w', encoding='utf-8') as f:
    json.dump(include, f, ensure_ascii=False, indent=4)
    print("include.json is generated.")
