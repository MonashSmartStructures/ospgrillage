from GrillageGenerator import GrillageGenerator, OPMemberProp
import pickle
import openseespy.opensees as ops
# import xlsxwriter
import matplotlib.pyplot as plt
from PlotWizard import *

# construct op grillage object
test_bridge = GrillageGenerator(bridge_name="Example_superT_10m", long_dim=10, width=5, skew=-11,
                                num_long_grid=4, num_trans_grid=13, cantilever_edge=1, mesh_type="Ortho")

# define material
test_bridge.material_definition(mat_type="Concrete01", mat_vec=[-6.0, -0.004, -6.0, -0.014])
test_bridge.op_uniaxial_material()

# connectivity generation
# user to define each member prop object (OPMemberProp) and pass it through GrillageGenerator.op_create_elements
longmem = OPMemberProp(1, 1, 0.896, 3.47E+10, 2.00E+10, 0.133, 0.213, 0.259, 0.233, 0.58, principal_angle=0)
longmem_prop = longmem.get_section_input()
long_tag = 1
skew_tag = 2
trans_tag = 3
test_bridge.op_create_elements(longmem_prop, long_tag, longmem.beam_ele_type, member='long_mem')

# edge
edge = OPMemberProp(2, 1, 0.044625, 3.47E+10, 2.00E+10, 2.6e-4, 1.1e-4, 2.42e-4, 3.72e-2, 3.72e-2, principal_angle=0)
edge_prop = edge.get_section_input()
test_bridge.op_create_elements(edge_prop, long_tag, edge.beam_ele_type, member='long_edge_1')

# Trans
trans = OPMemberProp(2, 1, 0.04428, 3.47E+10, 2.00E+10, 2.28e-3, 2.23e-1, 1.2e-3, 3.69e-1, 3.69e-1, principal_angle=0)
trans_prop = trans.get_section_input()
test_bridge.op_create_elements(trans_prop, skew_tag, edge.beam_ele_type, member='trans_mem')

# Trans edge1
transedge1 = OPMemberProp(2, 1, 0.02214, 3.47E+10, 2.00E+10, 2.17e-3, 1.11e-1, 5.97e-4, 1.85e-1, 1.85e-1,
                          principal_angle=0)
transedge1_prop = transedge1.get_section_input()
test_bridge.op_create_elements(transedge1_prop, skew_tag, edge.beam_ele_type, member='trans_edge_1')

transedge2 = OPMemberProp(2, 1, 0.02214, 3.47E+10, 2.00E+10, 2.17e-3, 1.11e-1, 5.97e-4, 1.85e-1, 1.85e-1,
                          principal_angle=0)
transedge2_prop = transedge2.get_section_input()
test_bridge.op_create_elements(transedge2_prop, skew_tag, edge.beam_ele_type, member='trans_edge_2')

# option for user to output bridge nodes and connectivity data
test_bridge.compile_output("test_bridge")
# plot nodes
x = [sub[1] for sub in test_bridge.Nodedata]
y = [sub[3] for sub in test_bridge.Nodedata]
print(type(x[1]))
model = plt.scatter(x, y)
plt.axis('equal')

# plot elements
plot_section(test_bridge, test_bridge.long_edge_1)
plot_section(test_bridge,test_bridge.long_mem)
plot_section(test_bridge, test_bridge.trans_mem)
plot_section(test_bridge, test_bridge.trans_edge_1)
plot_section(test_bridge, test_bridge.trans_edge_2)

plt.show()

# workbook = xlsxwriter.Workbook('arrays.xlsx')
# worksheet = workbook.add_worksheet()
#
# row = 0
#
# for col, data in enumerate(testbridge.Nodedata):
#     worksheet.write_column(row, col, data)
#
# workbook.close()
