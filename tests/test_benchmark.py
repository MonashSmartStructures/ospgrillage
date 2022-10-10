#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This test contains a validation against a numerical bridge model made in LUSAS software. Note the test portion of this file are
specific to the comparison i.e. 28m model between LUSAS model outputs and ospg outputs - hence is not advisable to copy-paste
the tests herein to for another new pytest (say another model). However it is reasonable to replicate structure of the fixtures i.e.
the model creation and running analysis domain of the pytest.
"""
import pytest
import pickle
import json
import numpy as np
import pandas
import sys, os
import ospgrillage as ospg
from pathlib import Path

sys.path.insert(0, os.path.abspath("../"))


def create_json_bridge():
    bridge = {
        "grid": {
            "name": "Super-T 28m",
            "span": 28,
            "width": 10.175,
            "n_longit": 7,
            "n_trans": 11,
            "edge_dist": 1.0875,
            "angle": 0,
        },
        "material": {
            "mat_type": "concrete",
            "code_use": "AS5100-2017",
            "mat_grade": "50MPa",
            "E": 34.8,
            "G": 20,
        },
        "longitudinal": {
            "A": 0.866937,
            "J": 0.154806,
            "Iz": 0.215366,
            "Iy": 0.213602,
            "Az": 0.444795,
            "Ay": 0.258704,
        },
        "edge": {
            "A": 0.044625,
            "J": 0.26253e-3,
            "Iz": 0.241812e-3,
            "Iy": 0.113887e-3,
            "Az": 0.0371929,
            "Ay": 0.0371902,
        },
        "transverse": {
            "A": 0.504,
            "J": 5.22303e-3,
            "Iz": 1.3608e-3,
            "Iy": 0.32928,
            "Az": 0.42,
            "Ay": 0.42,
        },
        "end_slab": {
            "A": 0.252,
            "J": 2.5012e-3,
            "Iz": 0.6804e-3,
            "Iy": 0.04116,
            "Az": 0.21,
            "Ay": 0.21,
        },
        "load": 1,
        "load factors": [1.2, 1.5],
    }
    return bridge


@pytest.fixture()
def create_grillage():
    # Units #
    kilo = 1e3
    milli = 1e-3
    N = 1
    m = 1
    mm = milli * m
    m2 = m**2
    m3 = m**3
    m4 = m**4
    kN = kilo * N
    MPa = N / (mm**2)
    GPa = kilo * MPa

    # read json file for model inputs
    # with open('super_t_28.json') as f:
    #    bridge = json.load(f)

    try:
        with open("super_t_28.json") as f:
            bridge = json.load(f)
    except (FileNotFoundError, IOError):
        bridge = create_json_bridge()
    # material #
    material_prop = bridge["material"]

    # sections (lusas parameters)
    longit_prop = bridge["longitudinal"]
    edge_prop = bridge["edge"]
    trans_prop = bridge["transverse"]
    end_trans_prop = bridge["end_slab"]

    # grid #
    grid_prop = bridge["grid"]

    grid_name = grid_prop["name"]

    L = grid_prop["span"] * m  # span
    w = grid_prop["width"] * m  # width

    n_l = grid_prop["n_longit"]  # number of longitudinal members
    n_t = grid_prop["n_trans"]  # number of transverse members
    edge_dist = (
        grid_prop["edge_dist"] * m
    )  # distance between edge beam and first exterior beam
    angle = grid_prop["angle"]  # skew angle

    # loading #
    P = bridge["load"] * kN

    # load case names (also used as load names) #
    load_name = [
        "Line Test",
        "Points Test (Global)",
        "Points Test (Local)",
        "Patch Test",
        "Moving Two Axle Truck",
    ]

    # load combos (line with patch) #
    load_combo = {
        "name": "Load Combo",
        "factor_1": bridge["load factors"][0],
        "factor_2": bridge["load factors"][1],
    }

    # define material #
    concrete = ospg.create_material(
        material=material_prop["mat_type"],
        code=material_prop["code_use"],
        grade=material_prop["mat_grade"],
    )

    # define sectons #

    longitudinal_section = ospg.create_section(
        A=longit_prop["A"] * m2,
        J=longit_prop["J"] * m3,
        Iz=longit_prop["Iz"] * m4,
        Iy=longit_prop["Iy"] * m4,
        Az=longit_prop["Az"] * m2,
        Ay=longit_prop["Ay"] * m2,
    )

    edge_longitudinal_section = ospg.create_section(
        A=edge_prop["A"] * m2,
        J=edge_prop["J"] * m3,
        Iz=edge_prop["Iz"] * m4,
        Iy=edge_prop["Iy"] * m4,
        Az=edge_prop["Az"] * m2,
        Ay=edge_prop["Ay"] * m2,
    )

    transverse_section = ospg.create_section(
        A=trans_prop["A"] * m2,
        J=trans_prop["J"] * m3,
        Iz=trans_prop["Iz"] * m4,
        Iy=trans_prop["Iy"] * m4,
        Az=trans_prop["Az"] * m2,
        Ay=trans_prop["Ay"] * m2,
        unit_width=True,
    )

    end_tranverse_section = ospg.create_section(
        A=end_trans_prop["A"] * m2,
        J=end_trans_prop["J"] * m3,
        Iz=end_trans_prop["Iz"] * m4,
        Iy=end_trans_prop["Iy"] * m4,
        Az=end_trans_prop["Az"] * m2,
        Ay=end_trans_prop["Ay"] * m2,
    )

    # define grillage members #
    longitudinal_beam = ospg.create_member(
        section=longitudinal_section, material=concrete
    )
    edge_longitudinal_beam = ospg.create_member(
        section=edge_longitudinal_section, material=concrete
    )

    transverse_slab = ospg.create_member(section=transverse_section, material=concrete)
    end_tranverse_slab = ospg.create_member(
        section=end_tranverse_section, material=concrete
    )

    # Create grid #
    simple_grid = ospg.create_grillage(
        bridge_name=grid_name,
        long_dim=L,
        width=w,
        skew=angle,
        num_long_grid=n_l,
        num_trans_grid=n_t,
        edge_beam_dist=edge_dist,
    )

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

    return simple_grid, bridge


@pytest.fixture()
def add_analysis_to_simple_grid(create_grillage):
    kilo = 1e3
    milli = 1e-3
    N = 1
    m = 1
    mm = milli * m
    m2 = m**2
    m3 = m**3
    m4 = m**4
    kN = kilo * N
    MPa = N / ((mm) ** 2)
    GPa = kilo * MPa
    simple_grid, bridge = create_grillage

    grid_prop = bridge["grid"]
    L = grid_prop["span"] * m  # span
    w = grid_prop["width"] * m  # width
    n_l = grid_prop["n_longit"]  # number of longitudinal members
    n_t = grid_prop["n_trans"]  # number of transverse members
    edge_dist = (
        grid_prop["edge_dist"] * m
    )  # distance between edge beam and first exterior beam
    angle = grid_prop["angle"]  # skew angle

    ## loading
    P = -bridge["load"] * kN
    # P = - 0.5 * kN

    ## load case names (also used as load names)
    load_name = [
        "Line Test",
        "Points Test (Global)",
        "Points Test (Local)",
        "Patch Test",
        "Moving Two Axle Truck",
    ]

    ## load combos (line with patch)
    load_combo = {
        "name": "Load Combo",
        "factor_1": bridge["load factors"][0],
        "factor_2": bridge["load factors"][1],
    }

    # opsv.plot_model("nodes") # plotting of grid for visualisation

    # Loading #

    # Line load running along midspan width (P is kN/m)
    line_point_1 = ospg.create_load_vertex(x=L / 2, z=0, p=P)
    line_point_2 = ospg.create_load_vertex(x=L / 2, z=w, p=P)
    test_line_load = ospg.create_load(
        loadtype="line", name=load_name[0], point1=line_point_1, point2=line_point_2
    )

    line_case = ospg.create_load_case(name=load_name[0])
    line_case.add_load(test_line_load)
    simple_grid.add_load_case(line_case)

    # Compound Point loads running along midspan at node points

    n_int = n_l - 4  # number of interior members
    space = (w - 2 * edge_dist) / (n_int + 1)  # spacing of interior members

    p_list = [0, edge_dist]
    for s in range(0, n_int):
        p_list.append(edge_dist + space * (s + 1) * m)
    p_list += [w - edge_dist, w]  # include other members nodes

    # in global
    test_points_load = ospg.create_compound_load(name=load_name[1])

    for p in p_list:
        point = ospg.create_load(
            loadtype="point",
            name="Point",
            point1=ospg.create_load_vertex(x=L / 2, z=p, p=P),
        )
        test_points_load.add_load(load_obj=point)

    points_case = ospg.create_load_case(name=load_name[1])
    points_case.add_load(test_points_load)
    simple_grid.add_load_case(points_case)

    # in local
    test_points_load = ospg.create_compound_load(name=load_name[2])

    for p in p_list:
        point = ospg.create_load(
            loadtype="point",
            name="Point",
            point1=ospg.create_load_vertex(x=0, z=p, p=P),
        )
        test_points_load.add_load(load_obj=point)

    test_points_load.set_global_coord(ospg.Point(L / 2, 0, 0))
    # shift from local to global

    points_case = ospg.create_load_case(name=load_name[2])
    points_case.add_load(test_points_load)
    simple_grid.add_load_case(points_case)

    # Patch load over entire bridge deck (P is kN/m2)
    patch_point_1 = ospg.create_load_vertex(x=0, z=0, p=P)
    patch_point_2 = ospg.create_load_vertex(x=L, z=0, p=P)
    patch_point_3 = ospg.create_load_vertex(x=L, z=w, p=P)
    patch_point_4 = ospg.create_load_vertex(x=0, z=w, p=P)
    test_patch_load = ospg.create_load(
        loadtype="patch",
        name=load_name[3],
        point1=patch_point_1,
        point2=patch_point_2,
        point3=patch_point_3,
        point4=patch_point_4,
    )

    patch_case = ospg.create_load_case(name=load_name[3])
    patch_case.add_load(test_patch_load)
    simple_grid.add_load_case(patch_case)

    # moving load  2 axle truck (equal loads, 2x2 spacing centre line running)

    # create truck in local coordinate system
    two_axle_truck = ospg.create_compound_load(name=load_name[4])
    point = ospg.create_load(
        loadtype="point",
        name="Point",
        point1=ospg.create_load_vertex(x=0, y=0, z=0, p=P),
    )

    axl_w = 2 * m  # axle width
    axl_s = 2 * m  # axle spacing
    veh_l = axl_s  # vehicle length

    xs = [0, 0, axl_s, axl_s]  # x-axis coordinates
    zs = [0, axl_w, axl_w, 0]  # z-axis coordinates

    for i, _ in enumerate(xs):
        truck_point = ospg.create_load_vertex(x=xs[i], z=zs[i], p=P)
        two_axle_truck.add_load(
            load_obj=ospg.create_load(
                loadtype="point", name="Point", point1=truck_point
            )
        )

    # create path object in global coordinate system
    # centre line running of entire span
    # increments so each case is one meter 1 m
    single_path = ospg.create_moving_path(
        start_point=ospg.Point(0 - axl_w, 0, w / 2 - axl_w / 2),
        end_point=ospg.Point(L, 0, w / 2 - axl_w / 2),
        increments=int((L + veh_l + 1) / 1),
    )
    # create moving load (and case)
    moving_truck = ospg.create_moving_load(name=load_name[4])
    # Set path and loads
    moving_truck.set_path(single_path)
    moving_truck.add_load(two_axle_truck)
    simple_grid.add_load_case(moving_truck)  # assign

    ## load combination
    load_combinations = {
        load_name[0]: load_combo["factor_1"],
        load_name[-2]: load_combo["factor_2"],
    }
    simple_grid.add_load_combination(
        load_combination_name=load_combo["name"],
        load_case_and_factor_dict=load_combinations,
    )

    # Run analysis #

    simple_grid.analyze()  # all load cases
    # simple_grid.analyze(load_case=load_name[0]) # specific load case
    # simple_grid.analyze(load_case=load_name[-1]) # specific moving load case

    all_results = simple_grid.get_results()
    # results = simple_grid.get_results(all=True) # same as above
    # results = simple_grid.get_results(load_case=load_case[0]) # specific load case
    move_results = simple_grid.get_results(
        load_case=load_name[-1]
    )  # specific moving load case
    combo_results = simple_grid.get_results(
        combinations=load_combinations
    )  # get combination

    return all_results, move_results, combo_results, bridge


def test_line_load_results(add_analysis_to_simple_grid):
    kilo = 1e3
    milli = 1e-3
    N = 1
    m = 1
    mm = milli * m
    m2 = m**2
    m3 = m**3
    m4 = m**4
    kN = kilo * N
    MPa = N / ((mm) ** 2)
    GPa = kilo * MPa
    # read from json file

    # ospg get results
    all_results, move_results, combo_results, bridge = add_analysis_to_simple_grid
    grid_prop = bridge["grid"]
    L = grid_prop["span"] * m  # span
    w = grid_prop["width"] * m  # width
    n_l = grid_prop["n_longit"]  # number of longitudinal members
    n_t = grid_prop["n_trans"]  # number of transverse members
    edge_dist = (
        grid_prop["edge_dist"] * m
    )  # distance between edge beam and first exterior beam
    angle = grid_prop["angle"]  # skew angle

    ## loading
    P = bridge["load"] * kN

    ## load case names (also used as load names)
    load_name = [
        "Line Test",
        "Points Test (Global)",
        "Points Test (Local)",
        "Patch Test",
        "Moving Two Axle Truck",
    ]

    ## load combos (line with patch)
    load_combo = {
        "name": "Load Combo",
        "factor_1": bridge["load factors"][0],
        "factor_2": bridge["load factors"][1],
    }

    axl_w = 2 * m  # axle width
    axl_s = 2 * m  # axle spacing
    veh_l = axl_s  # vehicle length

    ### Hand calculatioon checks ###

    hand_calcs = (
        [w * P * L / 4]
        + [n_l * P * L / 4] * 2
        + [
            w * P * L**2 / 8,
            2 * P * (L / 2 - axl_s / 2),
            load_combo["factor_1"] * w * P * L / 4
            + load_combo["factor_2"] * w * P * L**2 / 8,
        ]
    )
    # line, point, patch x 3, moving load, combination

    ele_set = list(range(84, 90 + 1))  # midspan members, i is the midspan node
    # static cases
    mid_sta = np.sum(
        np.array(
            all_results["forces"].sel(
                Loadcase=load_name[0:-1], Element=ele_set, Component="Mz_i"
            )
        ),
        axis=1,
    )
    # specific moving load case
    integer = int(L / 2 - 1 + 2)
    mid_mov = np.sum(
        np.array(
            move_results.forces.isel(Loadcase=integer).sel(
                Element=ele_set, Component="Mz_i"
            )
        )
    )

    # load combo
    mid_comb = np.sum(
        np.array(combo_results.forces.sel(Element=ele_set, Component="Mz_i"))
    )

    comp_calcs = list(mid_sta) + [mid_mov] + [mid_comb]

    diff = np.array(hand_calcs) - np.array(
        comp_calcs
    )  # diff between hand calcs and ospg

    # read pickle
    # var = pickle.load(open("Lusas_Outputs_cleaned.p", "rb"))

    # HARD CODE MAPPING - here specific for test_benchmark bridge and its ospg counterpart only
    # create mapping for nodes between LUSAS and ospg
    node_lusas = [
        1,
        3,
        5,
        7,
        9,
        11,
        13,
        15,
        17,
        19,
        21,
        33,
        35,
        37,
        39,
        41,
        43,
        45,
        47,
        49,
        51,
        53,
        65,
        67,
        69,
        71,
        73,
        75,
        77,
        79,
        81,
        83,
        85,
        97,
        99,
        101,
        103,
        105,
        107,
        109,
        111,
        113,
        115,
        117,
        129,
        131,
        133,
        135,
        137,
        139,
        141,
        143,
        145,
        147,
        149,
        161,
        163,
        165,
        167,
        169,
        171,
        173,
        175,
        177,
        179,
        181,
        193,
        195,
        197,
        199,
        201,
        203,
        205,
        207,
        209,
        211,
        213,
    ]
    node_ospg = [
        1,
        15,
        22,
        29,
        36,
        43,
        50,
        57,
        64,
        71,
        8,
        2,
        16,
        23,
        30,
        37,
        44,
        51,
        58,
        65,
        72,
        9,
        3,
        17,
        24,
        31,
        38,
        45,
        52,
        59,
        66,
        73,
        10,
        4,
        18,
        25,
        32,
        39,
        46,
        53,
        60,
        67,
        74,
        11,
        5,
        19,
        26,
        33,
        40,
        47,
        54,
        61,
        68,
        75,
        12,
        6,
        20,
        27,
        34,
        41,
        48,
        55,
        62,
        69,
        76,
        13,
        7,
        21,
        28,
        35,
        42,
        49,
        56,
        63,
        70,
        77,
        14,
    ]
    # create long ele matching dict for long ele , a is LUSAS, b is ospg
    a = [
        127,
        106,
        85,
        64,
        43,
        22,
        1,
        128,
        107,
        86,
        65,
        44,
        23,
        2,
        129,
        108,
        87,
        66,
        45,
        24,
        3,
        130,
        109,
        88,
        67,
        46,
        25,
        4,
        131,
        110,
        89,
        68,
        47,
        26,
        5,
        132,
        111,
        90,
        69,
        48,
        27,
        6,
        133,
        112,
        91,
        70,
        49,
        28,
        7,
        134,
        113,
        92,
        71,
        50,
        29,
        8,
        135,
        114,
        93,
        72,
        51,
        30,
        9,
        136,
        115,
        94,
        73,
        52,
        31,
        10,
    ]
    b = [
        25,
        24,
        23,
        22,
        21,
        20,
        19,
        38,
        37,
        36,
        35,
        34,
        33,
        32,
        51,
        50,
        49,
        48,
        47,
        46,
        45,
        64,
        63,
        62,
        61,
        60,
        59,
        58,
        77,
        76,
        75,
        74,
        73,
        72,
        71,
        90,
        89,
        88,
        87,
        86,
        85,
        84,
        103,
        102,
        101,
        100,
        99,
        98,
        97,
        116,
        115,
        114,
        113,
        112,
        111,
        110,
        129,
        128,
        127,
        126,
        125,
        124,
        123,
        136,
        135,
        134,
        133,
        132,
        131,
        130,
    ]
    match_long_ele = {
        a[i]: b[i] for i in range(len(a))
    }  # dict matching key (lusas ele) to value (ospg ele)

    # extract line load test LUSAS
    # line_load_result = var['3 Line Test Case']
    # extract line load test ospg

    # read from 28m result lusas
    point_lusas_disp_path = [
        "tests",
        "28m results",
        "28m_super_t_displacement",
        "2_Points_Test_Case.csv",
    ]
    line_lusas_disp_path = [
        "tests",
        "28m results",
        "28m_super_t_displacement",
        "3_Line_Test_Case.csv",
    ]
    line_lusas_force_path = [
        "tests",
        "28m results",
        "28m_super_t_forces",
        "3_Line_Test_Case.csv",
    ]
    print(Path.cwd())
    point_load_disp_lusas = pandas.read_csv(Path.cwd().joinpath(*point_lusas_disp_path))
    # get ospg point load case
    point_load_disp_ospg = all_results["displacements"].sel(
        Loadcase="Points Test (Global)",
        Component=["dx", "dy", "dz", "theta_x", "theta_y", "theta_z"],
    )

    # lusas elements are 3 noded beam elemnt, this function extracts only the end nodes (first and third) of the model.
    # user to provide node_lusas variable - a list containing the node number correspond to end nodes of beam elements
    lusas_def = reduce_lusas_node_result(
        pd_data=point_load_disp_lusas["DZ[m]"], node_to_extract_list=node_lusas
    )
    sorted_zip_ospg_node = sort_array_by_node_mapping(
        list_of_node=node_ospg,
        data_of_node=point_load_disp_ospg.sel(Component="dy").values,
    )

    line_load_disp_lusas = pandas.read_csv(Path.cwd().joinpath(*line_lusas_disp_path))
    lusas_def = reduce_lusas_node_result(
        pd_data=line_load_disp_lusas["DZ[m]"], node_to_extract_list=node_lusas
    )
    line_load_disp_ospg = all_results["displacements"].sel(
        Loadcase="Line Test",
        Component=["dx", "dy", "dz", "theta_x", "theta_y", "theta_z"],
    )
    sorted_zip_ospg_node = sort_array_by_node_mapping(
        list_of_node=node_ospg,
        data_of_node=line_load_disp_ospg.sel(Component="dy").values,
    )
    # lusas bending z
    line_load_force_lusas = pandas.read_csv(Path.cwd().joinpath(*line_lusas_force_path))
    single_component_line_lusas = extract_lusas_ele_forces(
        list_of_ele=a, df_force=line_load_force_lusas, component="My[N.m]"
    )
    # ospg bending z
    line_load_bendingz_ospg = (
        all_results["forces"]
        .sel(Loadcase="Line Test", Component=["Mz_i", "Mz_j"], Element=b)
        .values
    )
    # filter only the longitudinal members

    # assert deflection results , if all true/ isclose()
    assert sum(np.isclose(lusas_def, sorted_zip_ospg_node, atol=1e-5)) >= 77
    # assert  # line, point, patch x 3, moving load, combination bending moment about global Z axis close to hand calcs
    assert sum(np.isclose(hand_calcs, np.abs(comp_calcs))) >= 4  # TODO


# ---------------------------------------------
# static methods of test
# function to sort array of nodes based on a provided list of index / numbering. specify if list is either
# index or numbering
def sort_array_by_node_mapping(list_of_node, data_of_node, numbering=True):
    # note: list_of_node.size == data_of_node.size
    if numbering:  # numbering starts from 1
        list_of_node = [d - 1 for d in list_of_node]
        zip_element = zip(list_of_node, data_of_node)
    else:
        zip_element = zip(list_of_node, data_of_node)
    sorted_zip_element = sorted(zip_element)

    return [data_of_node[i] for i in list_of_node]


# function to extract data at node points corresponding to end nodes of element - this function is for model with
# beam elements having 3 or more nodes.
def reduce_lusas_node_result(pd_data, node_to_extract_list):
    return [
        element
        for counter, element in enumerate(pd_data)
        if counter + 1 in node_to_extract_list
    ]


def extract_lusas_ele_forces(list_of_ele, df_force, component: str):
    output = []
    for ele_num in list_of_ele:
        ele_output = []
        for index, row in df_force.iterrows():
            if row.Element == ele_num:
                # check if its intermediate node, if true, continue
                if all([index != 0, index != len(df_force) - 1]):
                    if (
                        not df_force.loc[index - 1].Element
                        == df_force.loc[index + 1].Element
                    ):
                        ele_output.append(row[component])
        output.append(ele_output)

    return output
