class Material:
    """
    Base class for Material objects
    """

    def __init__(self, mat_type, **kwargs):
        self.mat_type = mat_type
        self.op_mat_arg = None
        # assigns variables for all kwargs for specific material types , else sets None
        # properties for Concrete
        self.fpc = kwargs.get('fpc', None)
        self.epsc0 = kwargs.get('epsc0', None)
        self.fpcu = kwargs.get('fpcu', None)
        self.epcU = kwargs.get('epcU', None)

        # properties for Steel
        self.Fy = kwargs.get('Fy', None)
        self.E0 = kwargs.get('E0', None)
        self.b = kwargs.get('b', None)  # strain -hardening ratio.
        self.a1 = kwargs.get('a1', None)
        self.a2 = kwargs.get('a2', None)  # isotropic hardening parameter , see Ops Steel01
        self.a3 = kwargs.get('a3', None)
        self.a4 = kwargs.get('a4', None)


class UniAxialElasticMaterial(Material):
    """
    Main class for Opensees UniAxialElasticMaterial objects. This class acts as a wrapper to parse input parameters
    and returns command lines to generate the prescribe materials in Opensees material library.
    """

    def __init__(self, mat_type, **kwargs):
        # super(UniAxialElasticMaterial, self).__init__(length, length)
        super().__init__(mat_type, **kwargs)

    def get_uni_material_arg_str(self):
        if self.mat_type == "Concrete01":
            self.op_mat_arg = [self.fpc, self.epsc0, self.fpcu, self.epcU]
        elif self.mat_type == "Steel01":
            self.op_mat_arg = [self.Fy, self.E0, self.b, self.a1, self.a2, self.a3, self.a4]
        # check if None in entries
        if None in self.op_mat_arg:
            raise Exception(
                "parameters for Material: {} contains non numeric or missing parameter(s)".format(self.mat_type))
        return self.mat_type, self.op_mat_arg

    def get_uni_mat_ops_commands(self, material_tag):

        # e.g. concrete01 or steel01
        mat_str = None
        if self.mat_type == "Concrete01" or self.mat_type == "Steel01":
            mat_str = "ops.uniaxialMaterial(\"{type}\", {tag}, *{vec})\n".format(
                type=self.mat_type, tag=material_tag, vec=self.op_mat_arg)
        return mat_str


class NDmaterial(Material):
    """
    Main class for Opensees ND material object. This class wraps the ND material object by sorting input parameters and
    parse into input commands for ops commands.
    """

    def __init__(self, mat_type, **kwargs):
        super().__init__(mat_type, **kwargs)

    def get_ndMaterial_args(self):
        pass

    def get_nd_ops_commands(self):
        pass
