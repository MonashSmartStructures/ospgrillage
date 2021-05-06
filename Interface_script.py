from OpsGrillage import opGrillage, Section, GrillageMember, UniAxialElasticMaterial
# import xlsxwriter
from PlotWizard import *

# op-grillage module interface

# define material
concrete = UniAxialElasticMaterial(mat_type="Concrete01", mat_vec=[-6.0, -0.004, -6.0, -0.014])

# define sections
I_beam_section = Section(op_ele_type="elasticBeamColumn", A=0.896, E=3.47E+10, G=2.00E+10,
                         J=0.133, Iy=0.213, Iz=0.259,
                         Ay=0.233, Az=0.58)
slab_section = Section(op_ele_type="elasticBeamColumn", A=0.04428, E=3.47E+10, G=2.00E+10,
                       J=2.6e-4, Iy=1.1e-4, Iz=2.42e-4,
                       Ay=3.69e-1, Az=3.69e-1, unit_width=True)
exterior_I_beam_section = Section(op_section_type="Elastic", op_ele_type="elasticBeamColumn", A=0.044625, E=3.47E+10,
                                  G=2.00E+10, J=2.28e-3, Iy=2.23e-1,
                                  Iz=1.2e-3,
                                  Ay=3.72e-2, Az=3.72e-2)

# define member
I_beam = GrillageMember(name="Intermediate I-beams", section=I_beam_section, material=concrete)
slab = GrillageMember(name="concrete slab", section=slab_section, material=concrete)
exterior_I_beam = GrillageMember(name="exterior I beams", section=exterior_I_beam_section, material=concrete)

# construct op grillage object
test_bridge = opGrillage(bridge_name="SuperT_10m", long_dim=20, width=15, skew=-11,
                         num_long_grid=6, num_trans_grid=5, edge_beam_dist=1, mesh_type="Ortho")

# set material to grillage - to do add feature to check if material object is defined globally onto all elements
test_bridge.set_material(concrete)

# set grillage member
test_bridge.set_member(I_beam, member="interior_main_beam")
test_bridge.set_member(exterior_I_beam, member="exterior_main_beam_1")
test_bridge.set_member(exterior_I_beam, member="exterior_main_beam_2")
test_bridge.set_member(exterior_I_beam, member="edge_beam")
test_bridge.set_member(slab, member="transverse_slab")

# check output python file if executable
test_bridge.run_check()
# run simple gravity analysis
test_bridge.run_gravity_analysis(50)

# --------------------------------------------------------------------------------------------------------------------
# simple plotting commands
# plot by accessing Nodedata attribute
x = [sub[1] for sub in test_bridge.Nodedata]
y = [sub[3] for sub in test_bridge.Nodedata]
tag = [sub[0] for sub in test_bridge.Nodedata]
model = plt.scatter(x, y)
for point in range(0, len(x)):
    plt.text(x[point], y[point], tag[point], fontsize='xx-small')
plt.axis('equal')

# plot elements via assessing individual members (to be changed)
if test_bridge.mesh_type != "Ortho":  # skew
    plot_section(test_bridge, "interior_main_beam", 'r')
    plot_section(test_bridge, "transverse_slab", 'g')
    plot_section(test_bridge, "exterior_main_beam_1", 'b')
    plot_section(test_bridge, "exterior_main_beam_2", 'k')
    plot_section(test_bridge, "edge_beam", 'm')
    plot_section(test_bridge, "edge_slab", 'y')

else:  # orthogonal
    plot_section(test_bridge, "exterior_main_beam_1", 'b')
    plot_section(test_bridge, "exterior_main_beam_2", 'k')
    plot_section(test_bridge, "interior_main_beam", 'r')
    plot_section(test_bridge, "edge_beam", 'm')
    plot_section(test_bridge, "transverse_slab", 'g')
    plot_section(test_bridge, 7, 'c')
    plot_section(test_bridge, 8, 'm')
    plot_section(test_bridge, 9, 'b')
    plot_section(test_bridge, 10, 'k')
    plot_section(test_bridge, 5, 'r')
plt.show()
# # simple xls command to save bridge data
# workbook = xlsxwriter.Workbook('arrays.xlsx')
# worksheet = workbook.add_worksheet()
#
# row = 0
#
# for col, data in enumerate(testbridge.Nodedata):
#     worksheet.write_column(row, col, data)
#
# workbook.close()
