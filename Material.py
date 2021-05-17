class Material:
    """
    Class for material properties definition
    """

    def __init__(self, mat_type, mat_vec):
        # super(UniAxialElasticMaterial, self).__init__(length, length)
        self.mat_type = mat_type
        self.mat_vec = mat_vec


class UniAxialElasticMaterial(Material):
    """
    Class for uniaxial material prop
    """

    def __init__(self, mat_type, mat_vec):
        # super(UniAxialElasticMaterial, self).__init__(length, length)
        super().__init__(mat_type, mat_vec)

    def get_output_arguments(self):
        # TODO add additional uniaxialMaterial types
        # e.g. concrete01 or steel01
        pass
