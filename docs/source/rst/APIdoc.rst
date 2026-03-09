API reference
=============

Top-level interface functions
------------------------------

*ospgrillage* exposes a set of factory functions importable directly from the package.

.. autosummary::
   :toctree: generated/

   ospgrillage.material.create_material
   ospgrillage.members.create_section
   ospgrillage.members.create_member
   ospgrillage.osp_grillage.create_grillage
   ospgrillage.load.create_load_vertex
   ospgrillage.load.create_load
   ospgrillage.load.create_load_case
   ospgrillage.load.create_load_model
   ospgrillage.load.create_compound_load
   ospgrillage.load.create_moving_path
   ospgrillage.load.create_moving_load
   ospgrillage.mesh.create_point
   ospgrillage.postprocessing.create_envelope
   ospgrillage.postprocessing.plot_force
   ospgrillage.postprocessing.plot_defo

Grillage model API
------------------

Methods available on the :class:`~ospgrillage.osp_grillage.OspGrillage` object.

.. autosummary::
   :toctree: generated/

   ospgrillage.osp_grillage.OspGrillage.create_osp_model
   ospgrillage.osp_grillage.OspGrillage.set_member
   ospgrillage.osp_grillage.OspGrillage.set_boundary_condition
   ospgrillage.osp_grillage.OspGrillage.add_load_case
   ospgrillage.osp_grillage.OspGrillage.add_load_combination
   ospgrillage.osp_grillage.OspGrillage.analyze
   ospgrillage.osp_grillage.OspGrillage.get_results
   ospgrillage.osp_grillage.OspGrillage.get_nodes
   ospgrillage.osp_grillage.OspGrillage.get_element
   ospgrillage.osp_grillage.OspGrillage.clear_load_cases

Load module API
---------------

.. autosummary::
   :toctree: generated/

   ospgrillage.load.CompoundLoad.set_global_coord
   ospgrillage.load.CompoundLoad.add_load
   ospgrillage.load.LoadCase.add_load
   ospgrillage.load.MovingLoad.set_path
   ospgrillage.load.MovingLoad.add_load

OspGrillage class
-----------------

For design details see :doc:`ModuleDoc`.

.. autoclass:: ospgrillage.osp_grillage.OspGrillage
   :members:
   :show-inheritance:

OspGrillageBeam class
---------------------

.. autoclass:: ospgrillage.osp_grillage.OspGrillageBeam
   :members:
   :show-inheritance:

OspGrillageShell class
----------------------

.. autoclass:: ospgrillage.osp_grillage.OspGrillageShell
   :members:
   :show-inheritance:

Analysis class
--------------

.. autoclass:: ospgrillage.osp_grillage.Analysis
   :members:
   :show-inheritance:

Results class
-------------

.. autoclass:: ospgrillage.osp_grillage.Results
   :members:
   :show-inheritance:

Material class
--------------

.. autoclass:: ospgrillage.material.Material
   :members:
   :show-inheritance:

Section class
-------------

.. autoclass:: ospgrillage.members.Section
   :members:
   :show-inheritance:

GrillageMember class
--------------------

.. autoclass:: ospgrillage.members.GrillageMember
   :members:
   :show-inheritance:

Mesh class
----------

.. autoclass:: ospgrillage.mesh.Mesh
   :members:
   :show-inheritance:

Load classes
------------

NodalLoad
~~~~~~~~~

.. autoclass:: ospgrillage.load.NodalLoad
   :members:
   :show-inheritance:

PointLoad
~~~~~~~~~

.. autoclass:: ospgrillage.load.PointLoad
   :members:
   :show-inheritance:

LineLoading
~~~~~~~~~~~

.. autoclass:: ospgrillage.load.LineLoading
   :members:
   :show-inheritance:

PatchLoading
~~~~~~~~~~~~

.. autoclass:: ospgrillage.load.PatchLoading
   :members:
   :show-inheritance:

CompoundLoad
~~~~~~~~~~~~

.. autoclass:: ospgrillage.load.CompoundLoad
   :members:
   :show-inheritance:

MovingLoad
~~~~~~~~~~

.. autoclass:: ospgrillage.load.MovingLoad
   :members:
   :show-inheritance:

LoadCase
~~~~~~~~

.. autoclass:: ospgrillage.load.LoadCase
   :members:
   :show-inheritance:

LoadModel
~~~~~~~~~

.. autoclass:: ospgrillage.load.LoadModel
   :members:
   :show-inheritance:

Path
~~~~

.. autoclass:: ospgrillage.load.Path
   :members:
   :show-inheritance:

Post-processing classes
-----------------------

Envelope
~~~~~~~~

.. autoclass:: ospgrillage.postprocessing.Envelope
   :members:
   :show-inheritance:

PostProcessor
~~~~~~~~~~~~~

.. autoclass:: ospgrillage.postprocessing.PostProcessor
   :members:
   :show-inheritance:

ShapeFunction
~~~~~~~~~~~~~

.. autoclass:: ospgrillage.load.ShapeFunction
   :members:
   :show-inheritance:
