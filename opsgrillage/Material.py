import json


class Material:
    """
    Base class for Material objects
    """

    def __init__(self, **kwargs):
        self.mat_type = None  # this is the os convention for materials e.g. Concrete01
        self.op_mat_arg = None
        # assigns variables for all kwargs for specific material types , else sets None
        #
        self.code = kwargs.get("code","AS5100-2017")
        self.material_type = kwargs.get("type",None)
        self.material_grade = kwargs.get("grade",None)

        self.E = kwargs.get("E",None)
        self.G = kwargs.get("G",None)
        self.poisson = kwargs.get("v",None)

        # properties for Concrete
        self.fpc = kwargs.get("fpc", None)
        self.epsc0 = kwargs.get("epsc0", None)
        self.fpcu = kwargs.get("fpcu", None)
        self.epsU = kwargs.get("epsU", None)

        # properties for Steel
        self.Fy = kwargs.get("Fy", None)
        self.E0 = kwargs.get("E0", None)
        self.b = kwargs.get("b", None)  # strain -hardening ratio.
        self.a1 = kwargs.get("a1", None)
        self.a2 = kwargs.get(
            "a2", None
        )  # isotropic hardening parameter , see Ops Steel01
        self.a3 = kwargs.get("a3", None)
        self.a4 = kwargs.get("a4", None)

        self._mat_lib = self._read_mat_lib()
        self.parse_material_command()

    def parse_material_command(self):
        # function to parse the material inputs according to opensees inputs
        # if standardized material, use material library
        if self.code:
            with open('mat_lib.json', "r") as f:
                mat_lib = json.load(f)
                self.poisson = mat_lib[self.material_type][self.code][self.material_grade]['v']
                self.E = mat_lib[self.material_type][self.code][self.material_grade]['E']
                self.fpc = mat_lib[self.material_type][self.code][self.material_grade]['fc']
                self.density = mat_lib[self.material_type][self.code][self.material_grade]['rho']

        else:  # a custom material
            pass

        if self.G is None:
            self.G = self.E / (2 * (1 + self.poisson))  # if not G is defined, use formula to calculate G

        if self.material_type == "concrete":
            self.mat_type = "Concrete01"  # default opensees material type to represent concrete
        elif self.material_type == "steel":
            self.mat_type = "Steel01"  # default opensees material type to represent steel

    def get_material_args(self):
        # function to get material arguments. This function is handled by opsgrilalge during set_material
        if self.mat_type == "Concrete01":
            self.op_mat_arg = [self.fpc, self.epsc0, self.fpcu, self.epsU]
        elif self.mat_type == "Steel01":
            self.op_mat_arg = [self.Fy, self.E0, self.b, self.a1, self.a2, self.a3, self.a4]

        # TO ADD MORE materials

        # check if None in entries
        if None in self.op_mat_arg:
            raise Exception(
                "One or more missing/non-numeric parameters for Material: {} ".format(self.mat_type))
        return self.mat_type, self.op_mat_arg

    def _create_default_dict(self):
        """
        Just to make sure the JSON file is formatted correctly
        Note: 1 ksi = 6.89475728 MPa
        """

        mat_lib = {
            "concrete": {
                "AS5100-2017": {
                    "units": "SI",
                    "25MPa": {"fc": 25, "E": 26.7e9, "v": 0.2, "rho": 2.4e3},
                    "32MPa": {"fc": 32, "E": 30.1e9, "v": 0.2, "rho": 2.4e3},
                    "40MPa": {"fc": 40, "E": 32.8e9, "v": 0.2, "rho": 2.4e3},
                    "50MPa": {"fc": 50, "E": 34.8e9, "v": 0.2, "rho": 2.4e3},
                    "65MPa": {"fc": 65, "E": 37.4e9, "v": 0.2, "rho": 2.4e3},
                    "80MPa": {"fc": 80, "E": 39.6e9, "v": 0.2, "rho": 2.4e3},
                    "100MPa": {"fc": 100, "E": 42.2e9, "v": 0.2, "rho": 2.4e3},
                },
                "AASHTO-LRFD-8th": {
                    "units": "SI",
                    "2.4ksi": {"fc": 16.55, "E": 23.2223e9, "v": 0.2, "rho": 2.4027e3},
                    "3.0ksi": {"fc": 20.68, "E": 24.997e9, "v": 0.2, "rho": 2.4027e3},
                    "3.6ksi": {"fc": 24.82, "E": 26.547e9, "v": 0.2, "rho": 2.4027e3},
                    "4.0ksi": {"fc": 27.58, "E": 27.486e9, "v": 0.2, "rho": 2.4027e3},
                    "5.0ksi": {"fc": 34.47, "E": 29.587e9, "v": 0.2, "rho": 2.4027e3},
                    "6.0ksi": {"fc": 41.37, "E": 31.856e9, "v": 0.2, "rho": 2.4027e3},
                    "7.5ksi": {"fc": 51.71, "E": 34.999e9, "v": 0.2, "rho": 2.4027e3},
                    "10.0ksi": {"fc": 68.95, "E": 39.8e9, "v": 0.2, "rho": 2.4027e3},
                    "15.0ksi": {"fc": 103.42, "E": 48.582e9, "v": 0.2, "rho": 2.4027e3},
                },
            },
            "steel": {
                "AS5100.6-2004": {
                    "units": "SI",
                    "R250N": {"fy": 250, "E": 200.0e9, "v": 0.25, "rho": 7850},
                    "D500N": {"fy": 500, "E": 200.0e9, "v": 0.25, "rho": 7850},
                    "D500L": {"fy": 500, "E": 200.0e9, "v": 0.25, "rho": 7850},
                },
                "AASHTO-LRFD-8th": {
                    "units": "SI",
                    "A615-40": {"fy": 275.8, "E": 200.0e9, "v": 0.3, "rho": 7849},
                    "A615-60": {"fy": 413.67, "E": 200.0e9, "v": 0.3, "rho": 7849},
                    "A615-75": {"fy": 517.12, "E": 200.0e9, "v": 0.3, "rho": 7849},
                    "A615-80": {"fy": 551.58, "E": 200.0e9, "v": 0.3, "rho": 7849},
                    "A615-100": {"fy": 689.48, "E": 200.0e9, "v": 0.3, "rho": 7849},
                },
            },
        }

        return mat_lib

    def _write_mat_lib(self):
        """
        Write out the passed material dict
        Not to be used in the ordinary course of events at risk of overwriting
        manual edits to the mat_lib
        Used for initial creation of the mat_lib
        """

        with open("mat_lib.json", "w") as f:
            json.dump(self._mat_lib, f, indent=4)


    def _read_mat_lib(self):
        mat_lib = {}
        try:
            with open("mat_lib.json", "r") as f:
               mat_lib = json.load(f)
        except (FileNotFoundError, IOError):
            print("Material library unable to be read\nUsing default library")
            mat_lib = self._create_default_dict()
        return mat_lib


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
            self.op_mat_arg = [self.fpc, self.epsc0, self.fpcu, self.epsU]
        elif self.mat_type == "Steel01":
            self.op_mat_arg = [
                self.Fy,
                self.E0,
                self.b,
                self.a1,
                self.a2,
                self.a3,
                self.a4,
            ]
        # check if None in entries
        if None in self.op_mat_arg:
            raise Exception(
                "One or more missing/non-numeric parameters for Material: {} ".format(
                    self.mat_type
                )
            )
        return self.mat_type, self.op_mat_arg

    def get_uni_mat_ops_commands(self, material_tag):

        # e.g. concrete01 or steel01
        mat_str = None
        if self.mat_type == "Concrete01" or self.mat_type == "Steel01":
            mat_str = 'ops.uniaxialMaterial("{type}", {tag}, *{vec})\n'.format(
                type=self.mat_type, tag=material_tag, vec=self.op_mat_arg
            )
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




