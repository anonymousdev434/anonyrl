import json


include = {}
include["pre_euler3d_cpu.cpp"] = {}
include["pre_euler3d_cpu.cpp"]["function"] = {}
# add variables to exclude for each function
include["pre_euler3d_cpu.cpp"]["function"]["dump"] = ["variables", "data"]
include["pre_euler3d_cpu.cpp"]["function"]["copy"] = ["dst", "src"]
include["pre_euler3d_cpu.cpp"]["function"]["initialize_variables"] = ["variables"]
# include["pre_euler3d_cpu.cpp"]["function"]["compute_flux_contribution"] = ["momentumx", "momentumy", "momentumz", "density_energy", "pressure", "velocityx", "velocityy", "velocityz", "fc_momentumxx", "fc_momentumxy", "fc_momentumxz", "fc_momentumyx", "fc_momentumyy", "fc_momentumyz", "fc_momentumzx", "fc_momentumzy", "fc_momentumzz", "fc_density_energyx", "fc_density_energyy", "fc_density_energyz"]
include["pre_euler3d_cpu.cpp"]["function"]["compute_flux_contribution"] = []
# include["pre_euler3d_cpu.cpp"]["function"]["compute_velocity"] = ["density", "momentumx", "momentumy", "momentumz", "velocityx", "velocityy", "velocityz"]
include["pre_euler3d_cpu.cpp"]["function"]["compute_velocity"] = []
# include["pre_euler3d_cpu.cpp"]["function"]["compute_speed_sqd"] = ["velocityx", "velocityy", "velocityz"]
include["pre_euler3d_cpu.cpp"]["function"]["compute_speed_sqd"] = []
# include["pre_euler3d_cpu.cpp"]["function"]["compute_pressure"] = ["density","density_energy","speed_sqd"]
include["pre_euler3d_cpu.cpp"]["function"]["compute_pressure"] = []
# include["pre_euler3d_cpu.cpp"]["function"]["compute_speed_of_sound"] = ["density","pressure"]
include["pre_euler3d_cpu.cpp"]["function"]["compute_speed_of_sound"] = []
include["pre_euler3d_cpu.cpp"]["function"]["compute_step_factor"] = ["variables", "areas", "step_factors", "density", "velocityx", "velocityy", "velocityz", "density_energy", "momentumx", "momentumy", "momentumz", "speed_sqd", "pressure"]
include["pre_euler3d_cpu.cpp"]["function"]["compute_flux_contributions"] = ["variables", "fc_momentum_x", "fc_momentum_y", "fc_momentum_z", "fc_density_energy", "momentum_ix", "momentum_iy", "momentum_iz", "density_energy_i", "velocity_ix", "velocity_iy", "velocity_iz", "density_i", "pressure_i", "speed_sqd_i", "fc_i_momentum_xx", "fc_i_momentum_xy", "fc_i_momentum_xz", "fc_i_momentum_yx", "fc_i_momentum_yy", "fc_i_momentum_yz", "fc_i_momentum_zx", "fc_i_momentum_zy", "fc_i_momentum_zz", "fc_i_density_energyx", "fc_i_density_energyy", "fc_i_density_energyz"]
include["pre_euler3d_cpu.cpp"]["function"]["compute_flux"] = ["normals", "variables", "fc_momentum_x", "fc_momentum_y", "fc_momentum_z", "fc_density_energy", "fluxes", "momentum_ix", "momentum_iy", "momentum_iz", "density_i", "density_energy_i", "velocity_ix", "velocity_iy", "velocity_iz", "pressure_i", "density_nb", "momentum_nbx", "momentum_nby", "momentum_nbz", "density_energy_nb", "velocity_nbx", "velocity_nby", "velocity_nbz", "speed_sqd_i", "pressure_nb", "speed_sqd_nb"]
include["pre_euler3d_cpu.cpp"]["function"]["time_step"] = ["old_variables", "variables", "step_factors", "fluxes"]
include["pre_euler3d_cpu.cpp"]["function"]["main"] = ["areas", "normals", "variables", "old_variables", "step_factors", "fluxes", "fc_momentum_x", "fc_momentum_y", "fc_momentum_z", "fc_density_energy", "ff_momentumx", "ff_momentumy", "ff_momentumz", "ff_velocityx", "ff_velocityy", "ff_velocityz", "ff_pressure", "fc_momentumxx", "fc_momentumxy", "fc_momentumxz", "ff_fc_momentum_xx", "ff_fc_momentum_xy", "ff_fc_momentum_xz", "ff_fc_momentum_yx", "ff_fc_momentum_yy", "ff_fc_momentum_yz", "ff_fc_momentum_zx", "ff_fc_momentum_zy", "ff_fc_momentum_zz"]


# add global variables to include
include["pre_euler3d_cpu.cpp"]["global"] = [ "ff_fc_density_energyx", "ff_fc_density_energyy", "ff_fc_density_energyz"]





with open('include.json', 'w', encoding='utf-8') as f:
    json.dump(include, f, ensure_ascii=False, indent=4)
    print("include.json is generated.")
    