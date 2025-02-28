import json


include = {}
include["kmeans.cpp"] = {}
include["kmeans.cpp"]["function"] = {}
# add variables to exclude for each function
include["kmeans.cpp"]["function"]["euclid_dist_2"] = []
include["kmeans.cpp"]["function"]["find_nearest_point"] = []
include["kmeans.cpp"]["function"]["kmeans_clustering"] = []
include["kmeans.cpp"]["function"]["cluster"] = []
include["kmeans.cpp"]["function"]["main"] = []

# add global variables to include
include["kmeans.cpp"]["global"] = []


with open('include.json', 'w', encoding='utf-8') as f:
    json.dump(include, f, ensure_ascii=False, indent=4)
    print("include.json is generated.")
