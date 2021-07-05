class Material:
    """
    Base class for Material objects
    """

    def __init__(self, mat_type, mat_vec):
        # super(UniAxialElasticMaterial, self).__init__(length, length)
        self.mat_type = mat_type
        self.mat_vec = mat_vec


class UniAxialElasticMaterial(Material):
    """
    Main class for Opensees UniAxialElasticMaterial objects. This class acts as a wrapper to parse input parameters
    and returns command lines to generate the prescribe materials in Opensees library.
    """

    def __init__(self, mat_type, mat_vec):
        # super(UniAxialElasticMaterial, self).__init__(length, length)
        super().__init__(mat_type, mat_vec)

    def get_output_arguments(self):
        # TODO add additional uniaxialMaterial types
        # e.g. concrete01 or steel01
        pass
