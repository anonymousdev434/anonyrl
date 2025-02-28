import json


include = {}
include["kmeans.cpp"] = {}
include["kmeans.cpp"]["function"] = {}
# add variables to exclude for each function
include["kmeans.cpp"]["function"]["euclid_dist_2"] = ["pt1", "pt2"]
include["kmeans.cpp"]["function"]["find_nearest_point"] = ["pt", "pts"]
include["kmeans.cpp"]["function"]["kmeans_clustering"] = ["feature", "new_centers", "clusters", "partial_new_centers"]
include["kmeans.cpp"]["function"]["cluster"] = ["attributes", "cluster_centres", "tmp_cluster_centres"]
include["kmeans.cpp"]["function"]["main"] = ["buf", "attributes", "cluster_centres"]

# add global variables to include
include["kmeans.cpp"]["global"] = []


with open('include.json', 'w', encoding='utf-8') as f:
    json.dump(include, f, ensure_ascii=False, indent=4)
    print("include.json is generated.")
