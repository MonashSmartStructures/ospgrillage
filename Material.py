class Material:
    """
    Base class for Material objects
    """

    def __init__(self, mat_type, **kwargs):
        self.mat_type = mat_type
        self.op_mat_arg = None
        # assigns variables for all kwargs for specific material types , else sets None
        self.fpc = kwargs.get('fpc', None)
        self.epsc0 = kwargs.get('epsc0', None)
        self.fpcu = kwargs.get('fpcu', None)
        self.epcU = kwargs.get('epcU', None)

class UniAxialElasticMaterial(Material):
    """
    Main class for Opensees UniAxialElasticMaterial objects. This class acts as a wrapper to parse input parameters
    and returns command lines to generate the prescribe materials in Opensees library.
    """

    def __init__(self, mat_type, **kwargs):
        # super(UniAxialElasticMaterial, self).__init__(length, length)
        super().__init__(mat_type, **kwargs)

    def get_uni_material_arg_str(self):
        if self.mat_type == "Concrete01":
            self.op_mat_arg = [self.fpc, self.epsc0, self.fpcu, self.epcU]

        return self.mat_type, self.op_mat_arg

    def get_uni_mat_ops_commands(self,material_tag):

        # e.g. concrete01 or steel01
        mat_str = None
        if self.mat_type == "Concrete01":
            op_mat_arg = [self.fpc,self.epsc0,self.fpcu,self.epcU]
            mat_str = "ops.uniaxialMaterial(\"{type}\", {tag}, *{vec})\n".format(
                type=self.mat_type, tag=material_tag, vec=self.op_mat_arg)

        return mat_str


class NDmaterial(Material):
    def __init__(self,mat_type, **kwargs):
        super().__init__(mat_type, **kwargs)

    def get_ndMaterial_args(self):
        pass

    def get_nd_ops_commands(self):


        pass