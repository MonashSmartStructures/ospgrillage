import numpy as np
import ospgrillage as og

# Adopted units: N and m
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

# define material
concrete = og.create_material(material="concrete", code="AS5100-2017", grade="65MPa")

# define sections (parameters from LUSAS model)
edge_longitudinal_section = og.create_section(
    A=0.934 * m2,
    J=0.1857 * m3,
    Iz=0.3478 * m4,
    Iy=0.213602 * m4,
    Az=0.444795 * m2,
    Ay=0.258704 * m2,
)

longitudinal_section = og.create_section(
    A=1.025 * m2,
    J=0.1878 * m3,
    Iz=0.3694 * m4,
    Iy=0.113887e-3 * m4,
    Az=0.0371929 * m2,
    Ay=0.0371902 * m2,
)

transverse_section = og.create_section(
    A=0.504 * m2,
    J=5.22303e-3 * m3,
    Iy=0.32928 * m4,
    Iz=1.3608e-3 * m4,
    Ay=0.42 * m2,
    Az=0.42 * m2,
)

end_transverse_section = og.create_section(
    A=0.504 / 2 * m2,
    J=2.5012e-3 * m3,
    Iy=0.04116 * m4,
    Iz=0.6804e-3 * m4,
    Ay=0.21 * m2,
    Az=0.21 * m2,
)

# define grillage members
longitudinal_beam = og.create_member(section=longitudinal_section, material=concrete)
edge_longitudinal_beam = og.create_member(
    section=edge_longitudinal_section, material=concrete
)
transverse_slab = og.create_member(section=transverse_section, material=concrete)
end_transverse_slab = og.create_member(
    section=end_transverse_section, material=concrete
)

# parameters of bridge grillage
L = 33.5 * m  # span
w = 11.565 * m  # width
n_l = 7  # number of longitudinal members
n_t = 11  # number of transverse members
edge_dist = 1.05 * m  # distance between edge beam and first exterior beam
ext_to_int_dist = (
    2.2775 * m
)  # distance between first exterior beam and first interior beam
angle = 0  # skew angle
mesh_type = "Ortho"
# a new feature for multi span
spans = [9.144, 12.192, 9.144]  # list of float representing distance of each span
# spans = [L]

# create grillage
simple_grid = og.create_grillage(
    bridge_name="Super-T 33_5m",
    long_dim=L,
    width=w,
    skew=angle,
    num_long_grid=n_l,
    num_trans_grid=n_t,
    edge_beam_dist=edge_dist,
    ext_to_int_dist=ext_to_int_dist,
    mesh_type=mesh_type,
)

# assign grillage member to element groups of grillage model
simple_grid.set_member(longitudinal_beam, member="interior_main_beam")
simple_grid.set_member(longitudinal_beam, member="exterior_main_beam_1")
simple_grid.set_member(longitudinal_beam, member="exterior_main_beam_2")
simple_grid.set_member(edge_longitudinal_beam, member="edge_beam")
simple_grid.set_member(transverse_slab, member="transverse_slab")
simple_grid.set_member(end_transverse_slab, member="start_edge")
simple_grid.set_member(end_transverse_slab, member="end_edge")

# create the model in OpenSees
simple_grid.create_osp_model(
    pyfile=False
)  # pyfile will not (False) be generated for further analysis (should be create_osp?)
# og.opsplt.plot_model("nodes") # plotting using Get_rendering
og.opsv.plot_model(element_labels=0, az_el=(-90, 0))  # plotting using ops_vis
og.plt.show()

# reference unit load for various load types
P = 1 * kN
# name strings of load cases to be created
static_cases_names = [
    "Line Test Case",
    "Points Test Case (Global)",
    "Points Test Case (Local in Point)",
    "Points Test Case (Local in Compound)",
    "Patch Test Case",
]

# Line load running along midspan width (P is kN/m)
# Create vertical load points in global coordinate system
line_point_1 = og.create_load_vertex(x=L / 2, z=0, p=P)
line_point_2 = og.create_load_vertex(x=L / 2, z=w, p=P)
test_line_load = og.create_load(
    loadtype="line", name="Test Load", point1=line_point_1, point2=line_point_2
)

# Create load case, add loads, and assign
line_case = og.create_load_case(name=static_cases_names[0])
line_case.add_load(test_line_load)

simple_grid.add_load_case(line_case)

# Compound point loads along midspan width (P is kN)
# working in global coordinate system
p_list = [
    0,
    edge_dist,
    edge_dist + 2 * m,
    edge_dist + 4 * m,
    edge_dist + 6 * m,
    w - edge_dist,
    w,
]  # creating list of load position

test_points_load = og.create_compound_load(name="Points Test Case (Global)")

for p in p_list:
    point = og.create_load(
        loadtype="point", name="Point", point1=og.create_load_vertex(x=L / 2, z=p, p=P)
    )
    test_points_load.add_load(load_obj=point)

# Create load case, add loads, and assign
points_case = og.create_load_case(name=static_cases_names[1])
points_case.add_load(test_points_load)

simple_grid.add_load_case(points_case)

# Compound point loads along midspan width
# working in user-defined local coordinate (in point load)
test_points_load = og.create_compound_load(name="Points Test Case (Local in Point)")

for p in p_list:
    point = og.create_load(
        loadtype="point", name="Point", point1=og.create_load_vertex(x=0, z=p, p=P)
    )
    test_points_load.add_load(load_obj=point)

test_points_load.set_global_coord(og.Point(L / 2, 0, 0))  # shift from local to global

# Create load case, add loads, and assign
points_case = og.create_load_case(name=static_cases_names[2])
points_case.add_load(test_points_load)

simple_grid.add_load_case(points_case)

# Patch load over entire bridge deck (P is kN/m2)
patch_point_1 = og.create_load_vertex(x=0, z=0, p=P)
patch_point_2 = og.create_load_vertex(x=L, z=0, p=P)
patch_point_3 = og.create_load_vertex(x=L, z=w, p=P)
patch_point_4 = og.create_load_vertex(x=0, z=w, p=P)
test_patch_load = og.create_load(
    loadtype="patch",
    name="Test Load",
    point1=patch_point_1,
    point2=patch_point_2,
    point3=patch_point_3,
    point4=patch_point_4,
)

# Create load case, add loads, and assign
patch_case = og.create_load_case(name=static_cases_names[4])
patch_case.add_load(test_patch_load)
simple_grid.add_load_case(patch_case)

# 2 axle truck (equal loads, 2x2 spacing centre line running)
axl_w = 2 * m  # axle width
axl_s = 2 * m  # axle spacing
veh_l = axl_s  # vehicle length

# create truck in local coordinate system
two_axle_truck = og.create_compound_load(name="Two Axle Truck")
# note here we show that we can directly interact and create load vertex using LoadPoint namedtuple instead of create_load_vertex()
point1 = og.create_load(
    loadtype="point", name="Point", point1=og.LoadPoint(x=0, y=0, z=0, p=P)
)
point2 = og.create_load(
    loadtype="point", name="Point", point1=og.LoadPoint(x=0, y=0, z=axl_w, p=P)
)
point3 = og.create_load(
    loadtype="point", name="Point", point1=og.LoadPoint(x=axl_s, y=0, z=axl_w, p=P)
)
point4 = og.create_load(
    loadtype="point", name="Point", point1=og.LoadPoint(x=axl_s, y=0, z=0, p=P)
)

# add load to Compound load
two_axle_truck.add_load(load_obj=point1)
two_axle_truck.add_load(load_obj=point2)
two_axle_truck.add_load(load_obj=point3)
two_axle_truck.add_load(load_obj=point4)

# create path object in global coordinate system - centre line running of entire span
# when local coord: the path describes where the moving load *origin* is to start and end
single_path = og.create_moving_path(
    start_point=og.Point(0 - axl_w, 0, w / 2 - axl_w / 2),
    end_point=og.Point(L, 0, w / 2 - axl_w / 2),
    increments=int(np.round(L) + veh_l + 1),
)

# create moving load (and case)
moving_truck = og.create_moving_load(name="Moving Two Axle Truck")

# Set path to all loads defined within moving_truck
moving_truck.set_path(single_path)
# note: it is possible to set different paths for different compound loads in one moving load object
moving_truck.add_load(two_axle_truck)

# Assign
simple_grid.add_load_case(moving_truck)

simple_grid.analyze()
results = simple_grid.get_results()
og.plot_defo(simple_grid, results, member="exterior_main_beam_1", option="nodes")
og.plot_force(simple_grid, results, member="exterior_main_beam_1", component="Mz")

move_results = simple_grid.get_results(load_case="Moving Two Axle Truck")

print(move_results)

# Here is how to extract nodes of grillage elements
ele_set1 = simple_grid.get_element(member="exterior_main_beam_1")[0]
ele_set2 = simple_grid.get_element(member="exterior_main_beam_2")[0]
interior1 = simple_grid.get_element(member="interior_main_beam", z_group_num=2)[0]
interior2 = simple_grid.get_element(member="interior_main_beam", z_group_num=1)[0]
interior3 = simple_grid.get_element(member="interior_main_beam", z_group_num=0)[0]

# select the midspan longitudinal members i.e. members 84 to 90 in plot
ele_set = list(range(84, 90 + 1))
integer = int(
    L / 2 - 1 + 2
)  # here we choose when the load groups are at/near mid span L ~= 16.75m

# query for ele_set, component = Mz, (take ith node) and load case integer = 17
bending_z = np.sum(
    np.array(
        move_results.forces.isel(Loadcase=integer).sel(
            Element=ele_set, Component="Mz_i"
        )
    )
)

# Hand calc:
bending_z_theoretical = 2 * P * (L / 2 - axl_s / 2)  # 31500

print(bending_z)
print(bending_z_theoretical)
