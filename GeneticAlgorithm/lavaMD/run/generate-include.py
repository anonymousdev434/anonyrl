import json


include = {}
include["main.cpp"] = {}
include["main.cpp"]["function"] = {}
# add variables to exclude for each function
include["main.cpp"]["function"]["kernel_cpu"] = ["rAx","rAy","rAz","rAv","fAx","fAy","fAz","fAv","rBx","rBy","rBz","rBv","qB","rvx","rvy","rvz","rvv","qv","fvx","fvy","fvz","fvv"]
include["main.cpp"]["function"]["main"] = ["rv_cpux","rv_cpuy","rv_cpuz","rv_cpuv","qv_cpu","fv_cpux","fv_cpuy","fv_cpuz","fv_cpuv"]


# add global variables to include
include["main.cpp"]["global"] = ["par_alpha"]


with open('include.json', 'w', encoding='utf-8') as f:
    json.dump(include, f, ensure_ascii=False, indent=4)
    print("include.json is generated.")
