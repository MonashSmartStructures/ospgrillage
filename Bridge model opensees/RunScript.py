from GrillageGenerator import GrillageGenerator, OPMemberProp
import pickle
# import xlsxwriter
import matplotlib.pyplot as plt

# define grillage member prop



# OPmodel object
test_bridge = GrillageGenerator(bridge_name= "BenchMark", long_dim= 10,width=5,skew=13,
                                num_long_grid=4, num_trans_grid=13, cantilever_edge=1, mesh_type="Obllique")

# node generation
test_bridge.node_data_generation()
# connectivity generation

# input member properties

# define member properties to model
test_bridge.compile_output("test_bridge")
c = test_bridge.vector_xz_skew_mesh()
print(c)
x = [sub[1] for sub in test_bridge.Nodedata]
y = [sub[3] for sub in test_bridge.Nodedata]
print(type(x[1]))
model = plt.scatter(x,y)
plt.axis('equal')


def plot_section(ma_object, list_input):
    for num, ele in enumerate(list_input):
        matches_i_x = [x[1] for x in ma_object.Nodedata if ele[0] == x[0]]
        matches_i_z = [x[3] for x in ma_object.Nodedata if ele[0] == x[0]]
        matches_j_x = [x[1] for x in ma_object.Nodedata if ele[1] == x[0]]
        matches_j_z = [x[3] for x in ma_object.Nodedata if ele[1] == x[0]]
        plt.plot([matches_i_x, matches_j_x], [matches_i_z, matches_j_z])

plot_section(test_bridge,test_bridge.long_edge_1)
#plot_section(test_bridge,test_bridge.long_mem)
plot_section(test_bridge,test_bridge.trans_mem)
plot_section(test_bridge,test_bridge.trans_edge_1)
plot_section(test_bridge,test_bridge.trans_edge_2)

plt.show()
longmem = OPMemberProp(1,1,0.896,3.47E+10,2.00E+10,0.133,0.213,0.259,0.233,0.58,principal_angle = 0)
longmem_prop = longmem.get_section_input()
trans_tag = 1
test_bridge.op_create_elements(longmem_prop, trans_tag, longmem.beam_ele_type,expression='long_mem')


# workbook = xlsxwriter.Workbook('arrays.xlsx')
# worksheet = workbook.add_worksheet()
#
# row = 0
#
# for col, data in enumerate(testbridge.Nodedata):
#     worksheet.write_column(row, col, data)
#
# workbook.close()