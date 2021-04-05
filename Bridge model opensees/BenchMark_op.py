# Grillage generator wizard
# Model name: BenchMark
# Constructed on:05/04/2021 13:48:35
import numpy as np
import math
import openseespy.opensees as ops
import openseespy.postprocessing.Get_Rendering as opsplt
ops.wipe()
ops.model('basic', '-ndm', 3, '-ndf', 6)
