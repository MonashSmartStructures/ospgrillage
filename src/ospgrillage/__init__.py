import numpy as np  # re-exported: tests and users access ospgrillage.np
import openseespy.opensees as ops  # re-exported: tests and users access ospgrillage.ops
import opsvis as opsv  # re-exported: tests and users access ospgrillage.opsv
from ospgrillage.utils import *
from ospgrillage.mesh import *
from ospgrillage.load import *
from ospgrillage.material import *
from ospgrillage.members import *
from ospgrillage.osp_grillage import *
from ospgrillage.postprocessing import *

__version__ = "0.4.0"

# Explicit public API — everything a user should access from `import ospgrillage`
__all__ = [
    "__version__",
    # Grillage model
    "OspGrillage",
    "OspGrillageBeam",
    "OspGrillageShell",
    "create_grillage",
    # Members & sections
    "GrillageMember",
    "Section",
    "create_member",
    "create_section",
    # Materials
    "Material",
    "create_material",
    # Loads
    "LoadCase",
    "LoadModel",
    "Loads",
    "MovingLoad",
    "NodalLoad",
    "NodeForces",
    "PatchLoading",
    "Path",
    "PointLoad",
    "LineLoading",
    "LoadPoint",
    "CompoundLoad",
    "Line",
    "ShapeFunction",
    "create_load_vertex",
    "create_load",
    "create_load_case",
    "create_load_model",
    "create_moving_load",
    "create_moving_path",
    "create_compound_load",
    # Mesh / geometry
    "Point",
    "Mesh",
    "create_point",
    # Post-processing
    "Envelope",
    "PostProcessor",
    "create_envelope",
    "plot_force",
    "plot_defo",
]
