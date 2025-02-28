import json


include = {}
include["pre_euler3d_cpu.cpp"] = {}
include["pre_euler3d_cpu.cpp"]["function"] = {}
# add variables to exclude for each function
include["pre_euler3d_cpu.cpp"]["function"]["dump"] = []
include["pre_euler3d_cpu.cpp"]["function"]["copy"] = []
include["pre_euler3d_cpu.cpp"]["function"]["initialize_variables"] = []
include["pre_euler3d_cpu.cpp"]["function"]["compute_flux_contribution"] = []
include["pre_euler3d_cpu.cpp"]["function"]["compute_velocity"] = []
include["pre_euler3d_cpu.cpp"]["function"]["compute_speed_sqd"] = []
include["pre_euler3d_cpu.cpp"]["function"]["compute_pressure"] = []
include["pre_euler3d_cpu.cpp"]["function"]["compute_speed_of_sound"] = []
include["pre_euler3d_cpu.cpp"]["function"]["compute_step_factor"] = []
include["pre_euler3d_cpu.cpp"]["function"]["compute_flux_contributions"] = []
include["pre_euler3d_cpu.cpp"]["function"]["compute_flux"] = []
include["pre_euler3d_cpu.cpp"]["function"]["time_step"] = []
include["pre_euler3d_cpu.cpp"]["function"]["main"] = []


# add global variables to include
include["pre_euler3d_cpu.cpp"]["global"] = ["ff_variable", "ff_fc_momentum_xx", "ff_fc_momentum_xy", "ff_fc_momentum_xz", "ff_fc_momentum_yx", "ff_fc_momentum_yy", "ff_fc_momentum_yz", "ff_fc_momentum_zx", "ff_fc_momentum_zy", "ff_fc_momentum_zz", "ff_fc_density_energyx", "ff_fc_density_energyy", "ff_fc_density_energyz"]





with open('include.json', 'w', encoding='utf-8') as f:
    json.dump(include, f, ensure_ascii=False, indent=4)
    print("include.json is generated.")
