# Example module interface for ops-grillage
# import modules
from OpsGrillage import *
from PlotWizard import *

# define material
mat_vec=[-6.0, -0.004, -6.0, -0.014]
concrete = UniAxialElasticMaterial(mat_type="Concrete01", fpc=-6, epsc0=-0.004,fpcu=-6,epcU=-0.014)

# define sections
I_beam_section = Section(op_section_type="Elastic", op_ele_type="elasticBeamColumn", A=0.896, E=3.47E+10, G=2.00E+10,
                         J=0.133, Iy=0.213, Iz=0.259,
                         Ay=0.233, Az=0.58)
slab_section = Section(op_ele_type="elasticBeamColumn", A=0.04428, E=3.47E+10, G=2.00E+10,
                       J=2.6e-4, Iy=1.1e-4, Iz=2.42e-4,
                       Ay=3.69e-1, Az=3.69e-1, unit_width=True)
exterior_I_beam_section = Section(op_section_type="Elastic", op_ele_type="elasticBeamColumn", A=0.044625, E=3.47E+10,
                                  G=2.00E+10, J=2.28e-3, Iy=2.23e-1,
                                  Iz=1.2e-3,
                                  Ay=3.72e-2, Az=3.72e-2)

# define grillage members
I_beam = GrillageMember(member_name="Intermediate I-beams", section=I_beam_section, material=concrete)
slab = GrillageMember(member_name="concrete slab", section=slab_section, material=concrete)
exterior_I_beam = GrillageMember(member_name="exterior I beams", section=exterior_I_beam_section, material=concrete)

# construct grillage model
example_bridge = OpsGrillage(bridge_name="SuperT_10m", long_dim=10, width=7, skew=[42,0],
                             num_long_grid=7, num_trans_grid=5, edge_beam_dist=1, mesh_type="Ortho")
pyfile = False
example_bridge.create_ops(pyfile=pyfile)

# set material to grillage (globally) - comment to disable
example_bridge.set_material(concrete)

# set grillage member to element groups of grillage model
example_bridge.set_member(I_beam, member="interior_main_beam")
example_bridge.set_member(exterior_I_beam, member="exterior_main_beam_1")
example_bridge.set_member(exterior_I_beam, member="exterior_main_beam_2")
example_bridge.set_member(exterior_I_beam, member="edge_beam")
example_bridge.set_member(slab, member="transverse_slab")
example_bridge.set_member(exterior_I_beam, member="start_edge") # proxy
example_bridge.set_member(exterior_I_beam, member="end_edge")  # proxy
if not pyfile:
    opsplt.plot_model("nodes")
    pass

# ------------------------------------------------------------------------------------------------------------------
# Create loads, compound loads, moving loads

# Point load
location = LoadPoint(5, 0, 2, 20)  # create load point
Single = PointLoad(name="single point", point1=location)
front_wheel = PointLoad(name="front wheel", point1 = LoadPoint(2,0,2,50))
# Line load
barrierpoint_1 = LoadPoint(7.5, 0, 1, 2)
barrierpoint_2 = LoadPoint(7.5, 0, 6, 2)
Barrier = LineLoading("Barrier curb load", point1=barrierpoint_1, point2=barrierpoint_2)

# Patch load - lane loading
lane_point_1 = LoadPoint(0, 0, 3, 5)
lane_point_2 = LoadPoint(8, 0, 3, 5)
lane_point_3 = LoadPoint(8, 0, 5, 5)
lane_point_4 = LoadPoint(0, 0, 5, 5)
Lane = PatchLoading("Lane 1", point1=lane_point_1, point2=lane_point_2, point3=lane_point_3, point4=lane_point_4)

# compound load
M1600 = CompoundLoad("Lane and Barrier") # lane and barrier compounded
M1600.add_load(load_obj=Single, local_coord=Point(5,0,5))
M1600.add_load(load_obj=Barrier, local_coord=Point(3,0,5))
M1600.set_global_coord(Point(4,0,3))

# moving load
single_path = Path(start_point=Point(2,0,2), end_point= Point(4,0,3))  # create path object
move_point = MovingLoad(name="single_moving_point")
move_point.add_loads(load_obj=front_wheel,path_obj=single_path.get_path_points())
move_point.parse_moving_load_cases()
# --------------------------------------------------------------------------------------------------------------------
# Load Case
# if load added directly into load case - treat the coordinates as global
# if load is added to a compound load - the coordinates is treated as a local coordinate
ULS_DL = LoadCase(name="ULS-DL")
ULS_DL.add_load_groups(Lane)  # change here
example_bridge.add_load_case(ULS_DL)
example_bridge.analyse_load_case()


SLS_LL = LoadCase(name="Live traffic")
SLS_LL.add_load_groups(Single)
example_bridge.add_load_case(SLS_LL)

example_bridge.add_moving_load_case(move_point)
example_bridge.analyse_moving_load_case()
ba,ma = example_bridge.get_results()
print("finished ")
# --------------------------------------------------------------------------------------------------------------------

