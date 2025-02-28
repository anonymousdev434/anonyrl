import json


include = {}
include["blackscholes.cpp"] = {}
include["blackscholes.cpp"]["function"] = {}
# add variables to exclude for each function
include["blackscholes.cpp"]["function"]["main"] = []
include["blackscholes.cpp"]["function"]["bs_thread"] = []
include["blackscholes.cpp"]["function"]["BlkSchlsEqEuroNoDiv"] = []
include["blackscholes.cpp"]["function"]["CNDF"] = []

# add global variables to include
include["blackscholes.cpp"]["global"] = ["prices", "sptprice", "strike", "rate", "volatility", "otime", "inv_sqrt_2xPI", "zero", "half", "one", "const1", "const2", "const3", "const4", "const5", "const6"]


with open('include.json', 'w', encoding='utf-8') as f:
    json.dump(include, f, ensure_ascii=False, indent=4)
    print("include.json is generated.")
