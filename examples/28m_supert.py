import ospgrillage as og

pyfile = False

# metric units
m = 1.0
N = 1.0
sec = 1.0
MPa = 1e9 * N / m**2
g = 9.81 * m / sec**2  # 9.81 m/s2


# variables
E = 34.7 * MPa
G = 20e9 * MPa  # Pa
v = 0.3

q = 40e9 * N / m**2

L = 28 * m
H = 7 * m

# reference super T bridge 28m for validation purpose
# Members
concrete = og.create_material(
    mat_type="Concrete01", fpc=-6, epsc0=-0.004, fpcu=-6, epsU=-0.014
)
# define sections
super_t_beam_section = og.create_section(
    A=1.0447, J=0.230698, Iy=0.231329, Iz=0.533953, Ay=0.397032, Az=0.434351
)
transverse_slab_section = og.create_section(
    A=0.5372,
    E=E,
    G=G,
    J=2.79e-3,
    Iy=0.3988 / 2,
    Iz=1.45e-3 / 2,
    Ay=0.447 / 2,
    Az=0.447 / 2,
    unit_width=True,
)
end_tranverse_slab_section = og.create_section(
    A=0.5372 / 2,
    E=3.47e10,
    G=2.00e10,
    J=2.68e-3,
    Iy=0.04985,
    Iz=0.725e-3,
    Ay=0.223,
    Az=0.223,
)
edge_beam_section = og.Section(
    A=0.039375,
    E=3.47e10,
    G=2.00e10,
    J=0.21e-3,
    Iy=0.1e-3,
    Iz=0.166e-3,
    Ay=0.0328,
    Az=0.0328,
)

# define grillage members
super_t_beam = og.GrillageMember(
    member_name="Intermediate I-beams", section=super_t_beam_section, material=concrete
)
transverse_slab = og.GrillageMember(
    member_name="concrete slab", section=transverse_slab_section, material=concrete
)
edge_beam = og.GrillageMember(
    member_name="exterior I beams", section=edge_beam_section, material=concrete
)
end_tranverse_slab = og.GrillageMember(
    member_name="edge transverse", section=end_tranverse_slab_section, material=concrete
)

bridge_28 = og.OspGrillage(
    bridge_name="SuperT_28m",
    long_dim=L,
    width=H,
    skew=0,
    num_long_grid=7,
    num_trans_grid=14,
    edge_beam_dist=1.0875,
    mesh_type="Ortho",
)

# set grillage member to element groups of grillage model
bridge_28.set_member(super_t_beam, member="interior_main_beam")
bridge_28.set_member(super_t_beam, member="exterior_main_beam_1")
bridge_28.set_member(super_t_beam, member="exterior_main_beam_2")
bridge_28.set_member(edge_beam, member="edge_beam")
bridge_28.set_member(transverse_slab, member="transverse_slab")
bridge_28.set_member(end_tranverse_slab, member="start_edge")
bridge_28.set_member(end_tranverse_slab, member="end_edge")

# create the model instance
bridge_28.create_osp_model(pyfile=pyfile)

# Moving Load Analysis
front_wheel = og.PointLoad(
    name="front wheel", point1=og.LoadPoint(2, 0, 2, 50)
)  # Single point load 50 N
single_path = og.Path(
    start_point=og.Point(0, 0, 2), end_point=og.Point(29, 0, 3)
)  # create path object
move_point = og.MovingLoad(name="single_moving_point")
move_point.add_load(load_obj=front_wheel, path_obj=single_path.get_path_points())
move_point.parse_moving_load_cases()
bridge_28.add_moving_load_case(move_point)

# Analyze and get the results out
bridge_28.analyze("all")
non_moving_results, moving_load_results = bridge_28.get_results()

# Results
# extract the first element of the list (single element containing the data array)
moving_point_load_result = moving_load_results[0]
# Here we can slice data to get a reduced data array for the outputs
# query mid point shear force during truck movement
moving_point_load_result.sel(Node=63, Component="dy")
# query max of slice
moving_point_load_result.sel(Node=63, Component="dy").idxmax()
# query max and min envelopes of displacement for all nodes - this is done by max/min function across the 'Loadcase' dimension.
max_dY = moving_point_load_result.sel(Component="dy").max(dim="Loadcase")
min_dY = moving_point_load_result.sel(Component="dy").max(dim="Loadcase")
