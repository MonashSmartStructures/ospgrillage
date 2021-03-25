import pandas as pd
import numpy as np
import math
import openseespy.opensees as ops
from datetime import datetime


class GrillageGenerator:
    def __init__(self, bridge_name, long_dim, width, skew, num_long_grid,
                 num_trans_grid, cantilever_edge, mesh_type):
        self.mesh_type = mesh_type
        self.model_name = bridge_name
        # global dimensions of grillage
        self.long_dim = long_dim  # span , also c/c between support bearings
        self.width = width  # length of the bearing support - if skew  = 0 , this corresponds to width of bridge
        self.skew = skew  # angle in degrees
        # Properties of grillage
        self.num_long_gird = num_long_grid  # number of longitudinal beams
        self.num_trans_grid = num_trans_grid  # number of grids for transverse members
        self.edge_width = cantilever_edge  # width of cantilever edge beam

        # instantiate matrices for geometric dependent properties
        self.trans_dim = None  # to be calculated automatically based on skew
        self.breadth = None  # to be calculated automatically based on skew
        self.spclonggirder = None  # to be automated
        self.spctransslab = None  # to be automated
        # placeholder for nodes
        self.Nodedata = []  # array like to be populated
        self.nox = []
        self.noz = []
        # list containing elements of grillage model
        self.long_mem = []  #
        self.trans_mem = []
        self.long_edge_1 = []
        self.long_edge_2 = []
        self.trans_edge_1 = []
        self.trans_edge_2 = []  # np.array([],dtype="object")
        self.support_nodes = []  # to be populated by self.bound_cond_input
        self.concrete_prop = []
        self.steel_prop = []
        self.vxz_skew = []  # vector xz for skew members

        # rules for grillage automation - default values are in place, use keyword during class instantiation
        self.min_long_spacing = 1  # default 1m
        self.max_long_spacing = 2  # default 1m
        self.min_trans_spacing = 1  # default 1m
        self.max_trans_spacing = 2  # default 2m
        self.trans_to_long_spacing = 1  # default 1m
        self.min_grid_long = 9  # default 9 mesh odd number
        self.min_grid_trans = 5  # default 5 mesh odd number
        self.ortho_mesh = True  # boolean for grillages with skew < 15-20 deg
        self.y_elevation = 0  # default elevation of grillage wrt OPmodel coordinate system
        self.min_grid_ortho = 3  # for orthogonal mesh (skew>skew_threshold) region of orthogonal area default 3
        self.ndm = 3  # num model dimension - default 3
        self.ndf = 6  # num degree of freedom - default 6

        # default for support
        self.fix_val_pin = [1, 1, 1, 0, 0, 0]  # pinned
        self.fix_val_roller_x = [0, 1, 1, 0, 0, 0]  # roller
        # special rules for grillage - alternative to Properties of grillage definition - use for special dimensions
        self.nox_special = None  # array specifying custom coordinate of longitudinal nodes
        self.noz_special = None  # array specifying custom coordinate of transverse nodes
        self.skew_threshold = [10, 30]  # threshold for grillage to allow option of mesh choices
        # to be added
        # - special rule for multiple skew
        # - rule for multiple span + multi skew
        # - rule for pier

        # Wizard py file generation procedure
        # 0 construct py file and details
        self.filename = "{}_op.py".format(self.model_name)
        with open(self.filename, 'w') as file_handle:
            # create py file or overwrite existing
            # header of file
            file_handle.write("# Grillage generator wizard\n# Model name: {}\n".format(self.model_name))
            # to be fill in with other descriptions
            now = datetime.now()
            dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
            file_handle.write("# Constructed on:{}\n".format(dt_string))
            # imports
            file_handle.write("import numpy as np\nimport math\nimport openseespy.opensees as ops\n")

    # node functions
    def node_data_generation(self):
        # calculate grillage width
        self.trans_dim = self.width / math.cos(self.skew / 180 * math.pi)  # determine width of grillage
        # check for orthogonal mesh requirement
        self.check_skew()

        # 1 create Opensees model space
        self.op_model_space()
        # procedure to generate node and connectivity data of Opensees Model
        if self.ortho_mesh:
            print("orthogonal meshing, skew angle {} greater than threshold {} ".format(self.skew, self.skew_threshold))
            # perform orthogonal meshing
            self.orthogonal_mesh_automation()
            v = self.vector_xz_skew_mesh()
            # three ele transform for skew mesh
            self.op_ele_transform_input(1, [0, 0, 1])  # x dir members
            self.op_ele_transform_input(2, [v[0], 0, v[1]])  # z dir members (skew)
            self.op_ele_transform_input(3, [1, 0, 0])  # z dir members orthogonal
        else:  # skew mesh requirement
            print("skew meshing, skew angle {} less than threshold {} ".format(self.skew, self.skew_threshold))
            # perform skewed mesh
            self.skew_mesh_automation()
            v = self.vector_xz_skew_mesh()
            # two ele transformation for skew mesh
            self.op_ele_transform_input(1, [0, 0, 1])  # x dir members
            self.op_ele_transform_input(2, [v[0], 0, v[1]])  # z dir members (skew)

        # procedure to create bridge in Opensees software framework
        self.op_create_nodes()
        self.op_fix()

    #
    def boundary_cond_input(self, restraint_nodes, restraint_vector):
        """
        Function to define support boundary conditions of grillage model
        :param restraint_nodes: list of node tags to be restrained
        :param restraint_vector: list representing node restraint for Nx Ny Nz, Mx My Mz respectively.
                                    represented by 1 (fixed), and 0 (free)
        :return: populate self.support_node
        """
        for nodes in restraint_nodes:
            self.support_nodes.append([nodes, restraint_vector])

    def op_ele_transform_input(self, trans_tag, vector_xz, transform_type="Linear"):
        ops.geomTransf(transform_type, trans_tag, *vector_xz)
        with open(self.filename, 'a') as file_handle:
            file_handle.write("ops.geomTransf(\"{type}\", {tag}, *{vxz})\n".format(
                type=transform_type, tag=trans_tag, vxz=vector_xz))

    def check_skew_threshold(self, new_angle):
        self.skew_threshold = new_angle
        print("Skew mesh threshold (default 15) is modified to {}".format(self.skew_threshold))

    # functions to create bridge model in Opensees software
    def op_model_space(self):
        ops.model('basic', '-ndm', self.ndm, '-ndf', self.ndf)
        with open(self.filename, 'a') as file_handle:
            file_handle.write("ops.wipe()\n")
            file_handle.write("ops.model('basic', '-ndm', {ndm}, '-ndf', {ndf})\n".format(ndm=self.ndm, ndf=self.ndf))

    def op_create_nodes(self):
        for node_point in self.Nodedata:
            ops.node(node_point[0], node_point[1], node_point[2], node_point[3])
            with open(self.filename, 'a') as file_handle:
                file_handle.write("ops.node({tag}, {x}, {y}, {z})\n".format(tag=node_point[0],
                                                                            x=node_point[1], y=node_point[2],
                                                                            z=node_point[3]))
            # print("Node number: {} created".format(node_point[0]))

    def op_create_elements(self, op_member_prop_class, trans_tag, beam_ele_type, expression='long_mem'):
        # element list in attributes
        grillage_section = eval("self.{}".format(expression))

        #         element  tag   *[ndI ndJ]  A  E  G  Jx  Iy   Iz  transfOBJs
        for ele in grillage_section:
            ops.element(beam_ele_type, ele[3],
                        *[ele[0], ele[1]], *op_member_prop_class, trans_tag)  ###
            with open(self.filename, 'a') as file_handle:
                file_handle.write("ops.element(\"{type}\", {tag}, *[{i},{j}], *{memberprop},{transtag})\n"
                                  .format(type=beam_ele_type, tag=ele[3], i=ele[0], j=ele[1],
                                          memberprop=op_member_prop_class, transtag=trans_tag))

    def op_fix(self):
        for sup in self.trans_edge_1:
            ops.fix(sup[0], *self.fix_val_pin)
            with open(self.filename, 'a') as file_handle:
                file_handle.write("ops.fix({}, *{})\n".format(sup[0], self.fix_val_pin))
        for sup in self.trans_edge_2:
            ops.fix(sup[0], *self.fix_val_roller_x)
            with open(self.filename, 'a') as file_handle:
                file_handle.write("ops.fix({}, *{})\n".format(sup[0], self.fix_val_roller_x))

    # sub functions
    def vector_xz_skew_mesh(self):
        """
        Function to calculate vector xz used for geometric transformation of local section properties
        to match skew angle
        :return: vector parallel to plane xz of member (see geotransform Opensees) for skew members (member tag 5)
        """
        # rotated 90 deg clockwise (x,y) -> (y,-x)
        x = self.width
        y = -(-self.breadth)
        # normalize
        length = math.sqrt(x ** 2 + y ** 2)
        vec = [x / length, y / length]
        return vec

    def get_region_b(self, reg_a_end, step):
        """
        Function to calculate the node coordinate for skew region B
         -> triangular breadth along the longitudinal direction
        :param step: list containing transverse nodes (along z dir)
        :param reg_a_end: last node from regA (quadrilateral region)
        step
        :return: node coordinate for skew triangular area (region B1 or B2)
        """
        regB = [reg_a_end]  # initiate array regB
        for node in range(2, len(step)):  # minus 2 to ignore first and last element of step
            regB.append(self.long_dim - step[-node] * np.tan(self.skew / 180 * math.pi))
        # after append, add last element - self.long_dim
        regB.append(self.long_dim)
        regB = np.array(regB)
        return regB

    def check_skew(self):
        if self.mesh_type == "Ortho":
            self.ortho_mesh = True
        else:
            self.ortho_mesh = False

        # checks mesh type options are defined within the allowance threshold
        if self.skew <= self.skew_threshold[0] and self.ortho_mesh:
            # print
            raise Exception('Orthogonal mesh not allowed for angle less than {}'.format(self.skew_threshold[0]))
        elif self.skew >= self.skew_threshold[1] and not self.ortho_mesh:
            raise Exception('Oblique mesh not allowed for angle greater than {}'.format(self.skew_threshold[1]))

    def long_grid_nodes(self):
        """
        Function to output array of grid nodes along longitudinal direction
        :return: step: array/list containing node spacings along longitudinal direction (float)
        """

        last_girder = (self.width - self.edge_width)  # coord of last girder
        nox_girder = np.linspace(self.edge_width, last_girder, self.num_long_gird)
        step = np.hstack((np.hstack((0, nox_girder)), self.width))  # array containing z coordinate
        return step

    def skew_mesh_automation(self):
        if self.nox_special is None:  # check  special rule for slab spacing, else proceed automation of node
            self.nox = np.linspace(0, self.long_dim, self.num_trans_grid)  # array like containing node x cooridnate
        else:
            self.nox = self.nox_special  # assign custom array to nox array
        self.breadth = self.trans_dim * math.sin(self.skew / 180 * math.pi)  # length of skew edge in x dir
        step = self.long_grid_nodes()  # mesh points in z direction
        nodetagcounter = 1  # counter for nodetag
        eletagcounter = 1  # counter for eletag

        for pointz in step:  # loop for each mesh point in z dir
            noxupdate = self.nox - pointz * np.tan(
                self.skew / 180 * math.pi)  # get nox for current step in transverse mesh
            for pointx in noxupdate:  # loop for each mesh point in x dir (nox)
                # populate nodedata array - inputs [nodetag,x,y,z]
                self.Nodedata.append(
                    [nodetagcounter, pointx, self.y_elevation, pointz])  # NOTE here is where to change X Y plane
                nodetagcounter += 1

        for node_row_z in range(0, len(step)):
            for node_col_x in range(1, len(self.nox)):
                cumulative_row_z = node_row_z * len(self.nox)  # incremental nodes per step (node grid along transverse)
                next_cumulative_row_z = (node_row_z + 1) * len(
                    self.nox)  # increment nodes after next step (node grid along transverse)
                # procedure to create connectivity for x dir members
                if node_row_z == 0 or node_row_z == len(step) - 1:  # first and last row are edge beams
                    self.long_edge_1.append([cumulative_row_z + node_col_x, cumulative_row_z + node_col_x + 1,
                                             2, eletagcounter])  # record as edge beam with section 2
                    eletagcounter += 1
                else:
                    self.long_mem.append([cumulative_row_z + node_col_x, cumulative_row_z + node_col_x + 1,
                                          1, eletagcounter])  # record as longitudinal beam with section 1
                    eletagcounter += 1
                # procedure to create connectivity for z dir members (including skew members)
                if next_cumulative_row_z == nodetagcounter - 1:  # last row of line mesh z
                    pass
                elif cumulative_row_z + node_col_x - node_row_z * len(
                        self.nox) == 1:  # check if coincide with edge of line mesh z
                    self.trans_edge_1.append(
                        [cumulative_row_z + node_col_x, next_cumulative_row_z + node_col_x,
                         4, eletagcounter])  # record as edge slab with section 4
                    eletagcounter += 1
                else:
                    self.trans_mem.append([cumulative_row_z + node_col_x, next_cumulative_row_z + node_col_x,
                                           3, eletagcounter])  # record as slab with section 3
                    eletagcounter += 1
            if next_cumulative_row_z >= len(self.nox) * len(step):  # when loop last row
                pass
            else:
                self.trans_edge_2.append([cumulative_row_z + node_col_x + 1, next_cumulative_row_z + node_col_x + 1,
                                          4, eletagcounter])  # record opposite edge slab with section 4
                eletagcounter += 1
        print(self.trans_mem)

    def orthogonal_mesh_automation(self):
        # Note special rule for nox does not apply to orthogonal mesh - automatically calculates the optimal ortho mesh
        #             o o o o o o
        #           o
        #         o
        #       o o o o o o
        #         b    +  ortho
        self.breadth = self.trans_dim * math.sin(self.skew / 180 * math.pi)  # length of skew edge in x dir
        step = self.long_grid_nodes()  # mesh points in transverse direction

        # Generate nox based on two orthogonal region: (A)  quadrilateral area, and (B)  triangular area
        regA = np.linspace(0, self.long_dim - self.breadth, self.num_trans_grid)
        # RegA consist of overlapping last element
        # RegB first element overlap with RegA last element
        regB = self.get_region_b(regA[-1], step)
        self.nox = np.hstack((regA[:-1], regB))  # removed overlapping element

        # mesh region A quadrilateral area
        nodetagcounter = 1  # counter for nodetag

        for pointz in step:  # loop for each mesh point in z dir
            for pointx in regA[:-1]:  # loop for each mesh point in x dir (nox)
                # populate nodedata array - inputs [nodetag,x,y,z]
                self.Nodedata.append([nodetagcounter, pointx, self.y_elevation, pointz])
                nodetagcounter += 1

        # Elements mesh for region A
        for node_row_z in range(0, len(step)):
            for node_col_x in range(1, len(regA[:-1])):
                inc = node_row_z * len(regA[:-1])  # incremental nodes per step (node grid along transverse)
                next_inc = (node_row_z + 1) * len(
                    regA[:-1])  # increment nodes after next step (node grid along transverse)
                if node_row_z == 0 or node_row_z == len(step) - 1:  # first and last row are edge beams
                    self.long_edge_1.append(
                        [inc + node_col_x, inc + node_col_x + 1, 2])  # record as edge beam with section 2
                else:
                    self.long_mem.append(
                        [inc + node_col_x, inc + node_col_x + 1, 1])  # record as longitudinal beam with section 1
                if node_row_z != len(step) - 1:  # last row
                    self.trans_mem.append([inc + node_col_x, next_inc + node_col_x, 3])  # record as slab with section 3
            # last column of parallel
            if node_row_z != len(step) - 1:
                self.trans_mem.append(
                    [inc + node_col_x + 1, next_inc + node_col_x + 1, 4])  # record as slab with section 3
        print('Elements automation complete for region A')
        # mesh region B triangular area
        # B1 @ right support
        b1_node_tag_start = nodetagcounter - 1
        regBupdate = regB  # placeholder for mesh grid - to be updated during each loop
        for pointz in step:  # loop for each mesh point in z dir
            for pointx in regBupdate:  # loop for each mesh point in x dir (nox)
                self.Nodedata.append([nodetagcounter, pointx, self.y_elevation, pointz])
                nodetagcounter += 1
            regBupdate = regBupdate[:-1]  # remove last element for next step (skew boundary)

        # Elements mesh for region B1
        regBupdate = regB  # reset placeholder
        row_start = b1_node_tag_start
        reg_a_col = len(regA[:-1])  # ignore last element of reg A which overlap with regB
        for num_z in range(0, len(step)):
            # link nodes from region A
            if num_z == 0 or num_z == len(step) - 1:
                self.long_edge_1.append([reg_a_col, row_start + 1, 2])
            else:
                self.long_mem.append([reg_a_col, row_start + 1, 1])
            # loop for each column node in x dir
            for num_x in range(1, len(regBupdate)):
                if num_z == 0:  # first and last row are edge beams
                    self.long_edge_1.append(
                        [row_start + num_x, row_start + num_x + 1, 2])
                    # record as edge beam with section 2
                elif num_z != len(step) - 1:
                    self.long_mem.append(
                        [row_start + num_x, row_start + num_x + 1, 1])  # record as longitudinal beam with section 1
                # transverse member
                self.trans_mem.append([row_start + num_x, row_start + num_x + len(regBupdate), 5])  # transverse
            if num_z != len(step) - 1:  # last node of skew is single node, no element, break step
                self.trans_edge_2.append(
                    [row_start + num_x + 1, row_start + num_x + len(regBupdate), 6])  # support skew

            row_start = row_start + len(regBupdate)  # update next step start node
            regBupdate = regBupdate[:-1]  # remove last element for next step (skew boundary)
            reg_a_col = reg_a_col + len(regA[:-1])  # update next step node correspond with region A
        print('Elements automation complete for region B1 and A')

        # B2 left support
        regBupdate = -regB + regA[-1]  # left side of quadrilateral area, regB is now negative region
        for pointz in reversed(step):
            for pointx in regBupdate[1:]:  # remove counting first element overlap with region A
                self.Nodedata.append([nodetagcounter, pointx, self.y_elevation, pointz])
                nodetagcounter += 1
            regBupdate = regBupdate[:-1]  # remove last element (skew boundary) for next step

        # Element meshing for region B2
        # takes row_start from B1 auto meshing loop
        reg_a_col = 1 + (len(step) - 1) * len(regA[:-1])  # reset placeholder, start at node 1 for region B1
        regBupdate = -regB + regA[-1]  # reset placeholder
        for num_z in range(0, len(step)):
            # link nodes from region A
            if num_z == 0:
                self.long_edge_1.append([reg_a_col, row_start + 1, 2])
            else:
                self.long_mem.append([row_start + 1, reg_a_col, 1])
            # loop for each column node in x dir
            for num_x in range(1, len(regBupdate[1:])):
                if num_z == 0:  # first and last row are edge beams
                    self.long_edge_1.append([row_start + num_x + 1, row_start + num_x, 2])
                    # record as edge beam with section 2
                elif num_z != len(step) - 1:
                    self.long_mem.append(
                        [row_start + num_x + 1, row_start + num_x, 1])  # record as longitudinal beam with section 1
                # transverse member
                self.trans_mem.append([row_start + num_x, row_start + num_x + len(regBupdate[1:]), 5])  # transverse
            if num_z == len(step) - 2:
                self.trans_edge_1.append(
                    [1, row_start + len(regBupdate[1:]), 6])  # ele of node 1 to last node skew
            elif num_z != len(step) - 1:  # num of nodes = num ele + 1, thus ignore last step for implementing ele
                self.trans_edge_1.append(
                    [row_start + num_x + 1, row_start + num_x + len(regBupdate[1:]), 6])  # support skew
            # steps in transverse mesh, assign nodes of skew nodes

            row_start = row_start + len(regBupdate[1:])  # update next step start node
            regBupdate = regBupdate[:-1]  # remove last element for next step (skew boundary)
            reg_a_col = reg_a_col - len(regA[:-1])  # update next step node correspond with region A
        print('Elements automation complete for region B1 B2 and A')

    def compile_output(self, bridge_name):
        filename = "{}_properties.txt".format(bridge_name)
        with open(filename, 'w') as file_handle:
            # compile nodes
            file_handle.write("NODES\n")  # Header
            # file_handle.write(str(self.Nodedata))
            file_handle.writelines("%s\n" % nodes for nodes in self.Nodedata)  # Node data
            # compile connectivity
            file_handle.write("\nConnectivity\n")  # Header
            # write for each sections
            file_handle.write("long_mem \n")  # Sub_Header
            file_handle.writelines("%s\n" % ele for ele in self.long_mem)  #
            file_handle.write("long_edge_1\n")  # Sub_Header
            file_handle.writelines("%s\n" % ele for ele in self.long_edge_1)  #
            file_handle.write("long_edge_2\n")  # Sub_Header
            file_handle.writelines("%s\n" % ele for ele in self.long_edge_2)  #
            file_handle.write("trans_mem\n")  # Sub_Header
            file_handle.writelines("%s\n" % ele for ele in self.trans_mem)  #
            file_handle.write("trans_edge_1\n")  # Sub_Header
            file_handle.writelines("%s\n" % ele for ele in self.trans_edge_1)  #
            file_handle.write("trans_edge_2\n")  # Sub_Header
            file_handle.writelines("%s\n" % ele for ele in self.trans_edge_2)  #


# Member properties class
class OPMemberProp:
    def __init__(self, member_tag, trans_tag, A, E, G, J, Iy, Iz, Ay, Az,
                 principal_angle, beam_ele_type="elasticBeamColumn"):
        self.beam_ele_type = beam_ele_type
        self.principal_angle = principal_angle
        self.Az = Az
        self.Ay = Ay
        self.Iz = Iz
        self.Iy = Iy
        self.J = J
        self.G = G
        self.trans_tag = trans_tag  #
        self.member_tag = member_tag
        self.E = E
        self.A = A

    def get_section_input(self):
        """
        Function to obtain member attribute from OPMemberProp attribute.
        :return: section input for member section for input to Openseespy functions
        """
        section_input = None
        # assignment input based on ele type
        if self.beam_ele_type == "ElasticTimoshenkoBeam":
            section_input = [self.E, self.G, self.A, self.J, self.Iy, self.Iz, self.Ay, self.Az]
        elif self.beam_ele_type == "elasticBeamColumn":  # eleColumn
            section_input = [self.E, self.G, self.A, self.J, self.Iy, self.Iz]
        return section_input
