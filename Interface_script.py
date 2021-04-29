from opGrillage import opGrillage, Member, Section, GrillageMember, UniAxialElasticMaterial
# import xlsxwriter
from PlotWizard import *

# op-grillage module interface

# define material
concrete = UniAxialElasticMaterial(mat_type="Concrete01", mat_vec=[-6.0, -0.004, -6.0, -0.014])

# define sections
I_beam_section = Section(op_sec_tag='Elastic', A=0.896, E=3.47E+10, G=2.00E+10, J=0.133, Iy=0.213, Iz=0.259,
                         Ay=0.233, Az=0.58)

# define member
I_beam = GrillageMember(name="Intermediate I-beams", section_obj=I_beam_section, material_obj=concrete)

# define member (to be retired)
longmem_prop = Member("I-grider", 0.896, 3.47E+10, 2.00E+10, 0.133, 0.213, 0.259, 0.233, 0.58)
edge_prop = Member("cantilever_edges", 0.044625, 3.47E+10, 2.00E+10, 2.6e-4, 1.1e-4, 2.42e-4, 3.72e-2, 3.72e-2)
trans_prop = Member("slab", 0.04428, 3.47E+10, 2.00E+10, 2.28e-3, 2.23e-1, 1.2e-3, 3.69e-1, 3.69e-1)
transedge1_prop = Member("leftedgeslab", 0.02214, 3.47E+10, 2.00E+10, 2.17e-3, 1.11e-1, 5.97e-4, 1.85e-1, 1.85e-1)
transedge2_prop = Member("rightedgeslab", 0.02214, 3.47E+10, 2.00E+10, 2.17e-3, 1.11e-1, 5.97e-4, 1.85e-1, 1.85e-1)

# construct op grillage object
test_bridge = opGrillage(bridge_name="SuperT_10m", long_dim=10, width=5, skew=21,
                         num_long_grid=5, num_trans_grid=13, edge_beam_dist=1.5, mesh_type="Orth")
# print out names of members/groups
# string of groups - standard elements
#

# set material to grillage - to do add feature to check if material object is defined globally onto all elements
test_bridge.set_material(concrete)

# set grillage member
if test_bridge.ortho_mesh: # if ortho mesh is true
    test_bridge.set_grillage_members(longmem_prop, longmem_prop.op_ele_type, member="interior_main_beam")
    test_bridge.set_grillage_members(trans_prop, longmem_prop.op_ele_type, member="exterior_main_beam_1")
    test_bridge.set_grillage_members(longmem_prop, longmem_prop.op_ele_type, member="exterior_main_beam_2")
    test_bridge.set_grillage_members(longmem_prop, longmem_prop.op_ele_type, member="edge_beam")
# TODO : assign transverse members via unit length properties
else:  # skew mesh
    test_bridge.set_grillage_members(longmem_prop, longmem_prop.op_ele_type, member="interior_main_beam")
    test_bridge.set_grillage_members(trans_prop, longmem_prop.op_ele_type, member="transverse_slab")
    test_bridge.set_grillage_members(longmem_prop, longmem_prop.op_ele_type, member="edge_beam")
    test_bridge.set_grillage_members(trans_prop, longmem_prop.op_ele_type, member="exterior_main_beam_1")
    test_bridge.set_grillage_members(longmem_prop, longmem_prop.op_ele_type, member="exterior_main_beam_2")
    test_bridge.set_grillage_members(longmem_prop, longmem_prop.op_ele_type, member="edge_slab")

# check output python file if executable
test_bridge.run_check()
# run simple gravity analysis
test_bridge.run_gravity_analysis()

# --------------------------------------------------------------------------------------------------------------------
# simple plotting commands

# plot by accessing Nodedata attribute
x = [sub[1] for sub in test_bridge.Nodedata]
y = [sub[3] for sub in test_bridge.Nodedata]
model = plt.scatter(x, y)
plt.axis('equal')

# plot elements via assessing individual members (to be changed)
if test_bridge.mesh_type != "Ortho":
    plot_section(test_bridge, "interior_main_beam", 'r')
    plot_section(test_bridge, "transverse_slab", 'g')
    plot_section(test_bridge, "exterior_main_beam_1", 'b')
    plot_section(test_bridge, "exterior_main_beam_2", 'k')
    plot_section(test_bridge, "edge_beam", 'm')
    plot_section(test_bridge, "edge_slab", 'y')

else:
    plot_section(test_bridge, "exterior_main_beam_1", 'b')
    plot_section(test_bridge, "exterior_main_beam_2", 'k')
    plot_section(test_bridge, "interior_main_beam", 'r')
    #plot_section(test_bridge, "edge_beam", 'm')

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
