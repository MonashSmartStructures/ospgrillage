#!/usr/bin/env python
# coding: utf-8
import pytest
import pickle
import json
import numpy as np
# import openseespy.postprocessing.ops_vis as opsv

# importing ospgrillage
import sys

sys.path.append("E:\PostPhD\~Code\Python\Public\ops-grillage trials\ops-grillage")
import ospgrillage as ospg

@pytest.fixture()
def create_grillage():
    # Units #

    kilo = 1e3
    milli = 1e-3
    N = 1
    m = 1
    mm = milli * m
    m2 = m ** 2
    m3 = m ** 3
    m4 = m ** 4
    kN = kilo * N
    MPa = N / ((mm) ** 2)
    GPa = kilo * MPa

    # read json file for model inputs
    with open('super_t_28.json') as f:
        bridge = json.load(f)

    # material
    material_prop = bridge["material"]

    # sections (lusas parameters)
    longit_prop = bridge["longitudinal"]
    edge_prop = bridge["edge"]
    trans_prop = bridge["transverse"]
    end_trans_prop = bridge["end_slab"]

    ## grid
    grid_prop = bridge["grid"]

    grid_name = grid_prop["name"]
    L = grid_prop["span"] * m  # span
    w = grid_prop["width"] * m  # width
    n_l = grid_prop["n_longit"]  # number of longitudinal members
    n_t = grid_prop["n_trans"]  # number of transverse members
    edge_dist = grid_prop["edge_dist"] * m  # distance between edge beam and first exterior beam
    angle = grid_prop["angle"]  # skew angle

    ## loading
    P = bridge["load"] * kN

    ## load case names (also used as load names)
    load_name = ["Line Test",
                 "Points Test (Global)",
                 "Points Test (Local)",
                 "Patch Test",
                 "Moving Two Axle Truck"]

    ## load combos (line with patch)
    load_combo = {"name": "Load Combo",
                  "factor_1": bridge["load factors"][0],
                  "factor_2": bridge["load factors"][1]}

    # define material #
    concrete = ospg.create_material(type=material_prop["mat_type"],
                                    code=material_prop["code_use"],
                                    grade=material_prop["mat_grade"])

    # define sectons #

    longitudinal_section = ospg.create_section(A=longit_prop["A"] * m2,
                                               E=material_prop["E"] * GPa,
                                               G=material_prop["G"] * GPa,
                                               J=longit_prop["J"] * m3,
                                               Iz=longit_prop["Iz"] * m4,
                                               Iy=longit_prop["Iy"] * m4,
                                               Az=longit_prop["Az"] * m2,
                                               Ay=longit_prop["Ay"] * m2)

    edge_longitudinal_section = ospg.create_section(A=edge_prop["A"] * m2,
                                                    E=material_prop["E"] * GPa,
                                                    G=material_prop["G"] * GPa,
                                                    J=edge_prop["J"] * m3,
                                                    Iz=edge_prop["Iz"] * m4,
                                                    Iy=edge_prop["Iy"] * m4,
                                                    Az=edge_prop["Az"] * m2,
                                                    Ay=edge_prop["Ay"] * m2)

    transverse_section = ospg.create_section(A=trans_prop["A"] * m2,
                                             E=material_prop["E"] * GPa,
                                             G=material_prop["G"] * GPa,
                                             J=trans_prop["J"] * m3,
                                             Iz=trans_prop["Iz"] * m4,
                                             Iy=trans_prop["Iy"] * m4,
                                             Az=trans_prop["Az"] * m2,
                                             Ay=trans_prop["Ay"] * m2)

    end_tranverse_section = ospg.create_section(A=end_trans_prop["A"] * m2,
                                                E=material_prop["E"] * GPa,
                                                G=material_prop["G"] * GPa,
                                                J=end_trans_prop["J"] * m3,
                                                Iz=end_trans_prop["Iz"] * m4,
                                                Iy=end_trans_prop["Iy"] * m4,
                                                Az=end_trans_prop["Az"] * m2,
                                                Ay=end_trans_prop["Ay"] * m2)

    # define grillage members #
    longitudinal_beam = ospg.create_member(section=longitudinal_section,
                                           material=concrete)
    edge_longitudinal_beam = ospg.create_member(section=edge_longitudinal_section,
                                                material=concrete)

    transverse_slab = ospg.create_member(section=transverse_section,
                                         material=concrete)
    end_tranverse_slab = ospg.create_member(section=end_tranverse_section,
                                            material=concrete)

    # Create grid #
    simple_grid = ospg.create_grillage(bridge_name=grid_name, long_dim=L, width=w, skew=angle,
                                       num_long_grid=n_l, num_trans_grid=n_t, edge_beam_dist=edge_dist)

    # assign grillage member to element groups of grillage model #

    simple_grid.set_member(longitudinal_beam, member="interior_main_beam")
    simple_grid.set_member(longitudinal_beam, member="exterior_main_beam_1")
    simple_grid.set_member(longitudinal_beam, member="exterior_main_beam_2")

    simple_grid.set_member(edge_longitudinal_beam, member="edge_beam")

    simple_grid.set_member(transverse_slab, member="transverse_slab")
    simple_grid.set_member(end_tranverse_slab, member="start_edge")
    simple_grid.set_member(end_tranverse_slab, member="end_edge")

    simple_grid.create_osp_model(pyfile=False)
    ospg.opsplt.plot_model("element")
    return simple_grid


def test_analysis_simple_grid(create_grillage):
    kilo = 1e3
    milli = 1e-3
    N = 1
    m = 1
    mm = milli * m
    m2 = m ** 2
    m3 = m ** 3
    m4 = m ** 4
    kN = kilo * N
    MPa = N / ((mm) ** 2)
    GPa = kilo * MPa
    with open('super_t_28.json') as f:
        bridge = json.load(f)
    grid_prop = bridge["grid"]
    L = grid_prop["span"] * m  # span
    w = grid_prop["width"] * m  # width
    n_l = grid_prop["n_longit"]  # number of longitudinal members
    n_t = grid_prop["n_trans"]  # number of transverse members
    edge_dist = grid_prop["edge_dist"] * m  # distance between edge beam and first exterior beam
    angle = grid_prop["angle"]  # skew angle

    ## loading
    P = bridge["load"] * kN

    ## load case names (also used as load names)
    load_name = ["Line Test",
                 "Points Test (Global)",
                 "Points Test (Local)",
                 "Patch Test",
                 "Moving Two Axle Truck"]

    ## load combos (line with patch)
    load_combo = {"name": "Load Combo",
                  "factor_1": bridge["load factors"][0],
                  "factor_2": bridge["load factors"][1]}
    simple_grid = create_grillage
    # pyfile will not be generated for further analysis
    # opsv.plot_model("nodes") # plotting of grid for visualisation

    # Loading #

    ## Line load running along midspan width (P is kN/m)
    line_point_1 = ospg.create_load_vertex(x=L / 2, z=0, p=P)
    line_point_2 = ospg.create_load_vertex(x=L / 2, z=w, p=P)
    test_line_load = ospg.create_load(type='line',
                                      name=load_name[0],
                                      point1=line_point_1, point2=line_point_2)

    line_case = ospg.create_load_case(name=load_name[0])
    line_case.add_load_groups(test_line_load)
    simple_grid.add_load_case(line_case)

    ## Compound Point loads running along midspan at node points

    n_int = n_l - 4  # number of interior members
    space = (w - 2 * edge_dist) / n_int  # spacing of interior members

    p_list = [0, edge_dist]
    for s in range(0, n_int):
        p_list.append(edge_dist + space * (s + 1) * m)
    p_list += [w - edge_dist, w]  # include other members nodes

    ### in global
    test_points_load = ospg.create_compound_load(name=load_name[1])

    for p in p_list:
        point = ospg.create_load(type='point',
                                 name="Point",
                                 point1=ospg.create_load_vertex(x=L / 2, z=p, p=P))
        test_points_load.add_load(load_obj=point)

    points_case = ospg.create_load_case(name=load_name[1])
    points_case.add_load_groups(test_points_load)
    simple_grid.add_load_case(points_case)

    ### in local
    test_points_load = ospg.create_compound_load(name=load_name[2])

    for p in p_list:
        point = ospg.create_load(type='point',
                                 name="Point",
                                 point1=ospg.create_load_vertex(x=0, z=p, p=P))
        test_points_load.add_load(load_obj=point)

    test_points_load.set_global_coord(ospg.Point(L / 2, 0, 0))
    # shift from local to global

    points_case = ospg.create_load_case(name=load_name[2])
    points_case.add_load_groups(test_points_load)
    simple_grid.add_load_case(points_case)

    ## Patch load over entire bridge deck (P is kN/m2)
    patch_point_1 = ospg.create_load_vertex(x=0, z=0, p=P)
    patch_point_2 = ospg.create_load_vertex(x=L, z=0, p=P)
    patch_point_3 = ospg.create_load_vertex(x=L, z=w, p=P)
    patch_point_4 = ospg.create_load_vertex(x=0, z=w, p=P)
    test_patch_load = ospg.create_load(type='patch', name=load_name[3],
                                       point1=patch_point_1, point2=patch_point_2,
                                       point3=patch_point_3, point4=patch_point_4)

    patch_case = ospg.create_load_case(name=load_name[3])
    patch_case.add_load_groups(test_patch_load)
    simple_grid.add_load_case(patch_case)

    ## moving load  2 axle truck (equal loads, 2x2 spacing centre line running)

    # create truck in local coordinate system
    two_axle_truck = ospg.create_compound_load(name=load_name[4])
    point = ospg.create_load(type="point", name="Point",
                             point1=ospg.create_load_vertex(x=0, y=0, z=0, p=P))

    axl_w = 2 * m  # axle width
    axl_s = 2 * m  # axle spacing
    veh_l = axl_s  # vehicle length

    xs = [0, 0, axl_s, axl_s]  # x-axis coordinates
    zs = [0, axl_w, axl_w, 0]  # z-axis coordinates

    for i, _ in enumerate(xs):
        truck_point = ospg.create_load_vertex(x=xs[i], z=zs[i], p=P)
        two_axle_truck.add_load(load_obj=ospg.create_load(type="point",
                                                          name="Point",
                                                          point1=truck_point))

    # create path object in global coordinate system
    # centre line running of entire span
    # increments so each case is one meter 1 m
    single_path = ospg.create_moving_path(start_point=ospg.Point(0 - axl_w, 0, w / 2 - axl_w / 2),
                                          end_point=ospg.Point(L, 0, w / 2 - axl_w / 2),
                                          increments=int((L + veh_l + 1) / 1))
    # create moving load (and case)
    moving_truck = ospg.create_moving_load(name=load_name[4])
    # Set path and loads
    moving_truck.set_path(single_path)
    moving_truck.add_loads(two_axle_truck)
    simple_grid.add_load_case(moving_truck)  # assign

    ## load combination
    load_combinations = {load_name[0]: load_combo["factor_1"],
                         load_name[-2]: load_combo["factor_2"]}
    simple_grid.add_load_combination(load_combination_name=load_combo["name"],
                                     load_case_and_factor_dict=load_combinations)

    # Run analysis #

    simple_grid.analyze(all=True)  # all load cases
    # simple_grid.analyze(load_case=load_name[0]) # specific load case
    # simple_grid.analyze(load_case=load_name[-1]) # specific moving load case

    all_results = simple_grid.get_results()
    # results = simple_grid.get_results(all=True) # same as above
    # results = simple_grid.get_results(load_case=load_case[0]) # specific load case
    move_results = simple_grid.get_results(load_case=load_name[-1])  # specific moving load case
    combo_results = simple_grid.get_results(get_combinations=True)  # get combination

    ### Hand calculatioon checks ###

    hand_calcs = [-w * P * L / 4] + [-n_l * P * L / 4] * 2 + [-w * P * L ** 2 / 8, -2 * P * (L / 2 - axl_s / 2),
                                                              -load_combo["factor_1"] * w * P * L / 4 - load_combo[
                                                                  "factor_2"] * w * P * L ** 2 / 8]
    # line, point, patch x 3, moving load, combination


    ele_set = list(range(84, 90 + 1))  # midspan members, i is the midspan node
    # static cases
    mid_sta = np.sum(np.array(all_results['forces'].sel(Loadcase=load_name[0:-1],
                                                        Element=ele_set,
                                                        Component="Mz_i")), axis=1)
    # specific moving load case
    integer = int(L / 2 - 1 + 2)
    mid_mov = np.sum(np.array(move_results['forces'].isel(Loadcase=integer).sel(Element=ele_set,
                                                                                Component="Mz_i")))

    # load combo
    mid_comb = np.sum(np.array(combo_results[load_combo["name"]]['forces'].sel(Element=ele_set,
                                                                               Component="Mz_i")))

    comp_calcs = list(mid_sta) + [mid_mov] + [mid_comb]

    diff = np.array(hand_calcs) - np.array(comp_calcs)

    print(hand_calcs)
    print(comp_calcs)
    print(diff)

    # read pickle
    var = pickle.load(open("Lusas_Outputs_cleaned.p", "rb"))

    # create long ele matching dict for long ele , a is LUSAS, b is ospg
    a = [127, 106, 85, 64, 43, 22, 1, 128, 107, 86, 65, 44, 23, 2, 129, 108, 87, 66, 45, 24, 3, 130, 109, 88, 67, 46, 25, 4, 131, 110, 89, 68, 47, 26, 5, 132, 111, 90, 69, 48, 27, 6, 133, 112, 91, 70, 49, 28, 7, 134, 113, 92, 71, 50, 29, 8, 135, 114, 93, 72, 51, 30, 9, 136, 115, 94, 73, 52, 31, 10]
    b = [25, 24, 23, 22, 21, 20, 19, 38, 37, 36, 35, 34, 33, 32, 51, 50, 49, 48, 47, 46, 45, 64, 63, 62, 61, 60, 59, 58, 77, 76, 75, 74, 73, 72, 71, 90, 89, 88, 87, 86, 85, 84, 103, 102, 101, 100, 99, 98, 97, 116, 115, 114, 113, 112, 111, 110, 129, 128, 127, 126, 125, 124, 123, 137, 136, 135, 134, 133, 132, 131]


    match_long_ele = {a[i]:b[i] for i in range(len(a))}

    # extract line load test LUSAS
    line_load_result = var['3 Line Test Case']
    # extract line load test ospg
    all_results["forces"].sel(Loadcase='Line Test')