# Example module interface for ops-grillage
# import modules
from OpsGrillage import OpsGrillage, Section, GrillageMember, UniAxialElasticMaterial, LineLoading, PatchLoading, \
    NodalLoad
from PlotWizard import *
import openseespy.opensees as ops

# define material
concrete = UniAxialElasticMaterial(mat_type="Concrete01", mat_vec=[-6.0, -0.004, -6.0, -0.014])

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
example_bridge = OpsGrillage(bridge_name="SuperT_10m", long_dim=4, width=7, skew=-11,
                             num_long_grid=5, num_trans_grid=5, edge_beam_dist=1, mesh_type="Orth")

# set material to grillage -
example_bridge.set_material(concrete)

# set grillage member to element groups of grillage model
example_bridge.set_member(I_beam, member="interior_main_beam")
example_bridge.set_member(exterior_I_beam, member="exterior_main_beam_1")
example_bridge.set_member(exterior_I_beam, member="exterior_main_beam_2")
example_bridge.set_member(exterior_I_beam, member="edge_beam")
example_bridge.set_member(slab, member="transverse_slab")
example_bridge.set_member(exterior_I_beam, member="edge_slab")

# test output python file
example_bridge.run_check()
# add/replace a point load analysis
# create a NodeLoad object
NL = NodalLoad("node load", [0, -2000, 0, 0, 0, 0], node_tag=20)
NL_b = NodalLoad("node load", [0, -1000, 0, 0, 0, 0], node_tag=20)
LaneLoad = PatchLoading("Lane 1", load_value=-9, northing_lines=[3.8, 6.2])

# add NodeLoad object to load case
example_bridge.add_load_case("First Load", NL)
example_bridge.copy_load_case(NL, [2, 3])


# --------------------------------------------------------------------------------------------------------------------
# simple plotting commands
model = plot_nodes(example_bridge, plot_args=None)

# plot mesh showing element connectivity
if example_bridge.mesh_type != "Ortho":  # skew
    plot_section(example_bridge, "interior_main_beam", 'r')
    plot_section(example_bridge, "transverse_slab", 'g')
    plot_section(example_bridge, "exterior_main_beam_1", 'b')
    plot_section(example_bridge, "exterior_main_beam_2", 'k')
    plot_section(example_bridge, "edge_beam", 'm')
    plot_section(example_bridge, "edge_slab", 'y')

else:  # orthogonal
    plot_section(example_bridge, "exterior_main_beam_1", 'b')
    plot_section(example_bridge, "exterior_main_beam_2", 'k')
    plot_section(example_bridge, "interior_main_beam", 'r')
    plot_section(example_bridge, "edge_beam", 'm')
    plot_section(example_bridge, "transverse_slab", 'g')
    plot_section(example_bridge, 7, 'c')
    plot_section(example_bridge, 8, 'm')
    plot_section(example_bridge, 9, 'b')
    plot_section(example_bridge, 10, 'k')
    plot_section(example_bridge, 5, 'r')
plt.show()

opsplt.plot_model()
print(ops.eleNodes(20))
