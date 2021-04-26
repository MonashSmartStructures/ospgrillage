from opGrillage import opGrillage, Member, Section, GrillageMember
# import xlsxwriter
from PlotWizard import *

# op-grillage module interface


# construct op grillage object
test_bridge = opGrillage(bridge_name="SuperT_10m", long_dim=10, width=5, skew=-11,
                         num_long_grid=6, num_trans_grid=13, cantilever_edge=1, mesh_type="Orth")

# define material


# set material if material applies to all elements
test_bridge.set_uniaxial_material(mat_type="Concrete01", mat_vec=[-6.0, -0.004, -6.0, -0.014])

# define sections
# name, A, E, G, J, Iy, Iz, Ay, Az
I_beam = Section(op_sec_tag='Elastic',A=0.896, E=3.47E+10, G=2.00E+10, J=0.133, Iy=0.213, Iz=0.259, Ay=0.233, Az=0.58)

# define member (current version)

# define member (to be withdraw)
longmem_prop = Member("I-grider", 0.896, 3.47E+10, 2.00E+10, 0.133, 0.213, 0.259, 0.233, 0.58)
edge_prop = Member("cantilever_edges", 0.044625, 3.47E+10, 2.00E+10, 2.6e-4, 1.1e-4, 2.42e-4, 3.72e-2, 3.72e-2)
trans_prop = Member("slab", 0.04428, 3.47E+10, 2.00E+10, 2.28e-3, 2.23e-1, 1.2e-3, 3.69e-1, 3.69e-1)
transedge1_prop = Member("leftedgeslab", 0.02214, 3.47E+10, 2.00E+10, 2.17e-3, 1.11e-1, 5.97e-4, 1.85e-1, 1.85e-1)
transedge2_prop = Member("rightedgeslab", 0.02214, 3.47E+10, 2.00E+10, 2.17e-3, 1.11e-1, 5.97e-4, 1.85e-1, 1.85e-1)

# set members to grillage through set_grillage_member() function
# test_bridge.set_grillage_members(longmem_prop, long_tag, longmem_prop.beam_ele_type, member='long_mem')
# test_bridge.set_grillage_members(edge_prop, long_tag, edge_prop.beam_ele_type, member='long_edge_1')
# test_bridge.set_grillage_members(edge_prop, long_tag, edge_prop.beam_ele_type, member='long_edge_2')
# test_bridge.set_grillage_members(trans_prop, skew_tag, edge_prop.beam_ele_type, member='trans_mem')
# test_bridge.set_grillage_members(transedge1_prop, skew_tag, edge_prop.beam_ele_type, member='trans_edge_1')
# test_bridge.set_grillage_members(transedge2_prop, skew_tag, edge_prop.beam_ele_type, member='trans_edge_2')

# new version of set grillage function
test_bridge.set_grillage_long_mem(longmem_prop, longmem_prop.op_ele_type, group=3)
test_bridge.set_grillage_trans_mem(trans_prop, longmem_prop.op_ele_type, group=2)
print(test_bridge.support_nodes)
# check output python file if executable
test_bridge.run_check()
# run simple gravity analysis

# --------------------------------------------------------------------------------------------------------------------
# plotting commands

# plot nodes
x = [sub[1] for sub in test_bridge.Nodedata]
y = [sub[3] for sub in test_bridge.Nodedata]
# print(type(x[1]))
model = plt.scatter(x, y)
plt.axis('equal')

# plot elements
plot_section(test_bridge, test_bridge.long_edge_1, 'b')
plot_section(test_bridge, test_bridge.long_edge_2, 'k')
# plot_section(test_bridge, test_bridge.long_mem,'r')
# plot_section(test_bridge, test_bridge.trans_mem,'g')
# plot_section(test_bridge, test_bridge.trans_edge_1,'b')
# plot_section(test_bridge, test_bridge.trans_edge_2,'b')

plt.show()

# # xls commands
# workbook = xlsxwriter.Workbook('arrays.xlsx')
# worksheet = workbook.add_worksheet()
#
# row = 0
#
# for col, data in enumerate(testbridge.Nodedata):
#     worksheet.write_column(row, col, data)
#
# workbook.close()
