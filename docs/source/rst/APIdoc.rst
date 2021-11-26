====================
API reference
====================

User interface functions - API
------------------------------------------
*ospgrillage* comprised of user interface functions callable from the main module. Following section summarizes
the functions callable from all modules within *ospgrillage*.

Top level interface functions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autosummary::
    :toctree: generated/

    ospgrillage.material.create_material
    ospgrillage.members.create_section
    ospgrillage.members.create_member
    ospgrillage.osp_grillage.create_grillage
    ospgrillage.load.create_load_vertex
    ospgrillage.load.create_load
    ospgrillage.mesh.create_point
    ospgrillage.load.create_load_case
    ospgrillage.load.create_compound_load
    ospgrillage.load.create_moving_path
    ospgrillage.load.create_moving_load
    ospgrillage.postprocessing.plot_force
    ospgrillage.postprocessing.plot_defo
    ospgrillage.postprocessing.create_envelope


Grillage model interface API
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The following methods can be called on the :class:`ospgrillage.osp_grillage.OspGrillage` object.

.. autosummary::
    :toctree: generated/

    ospgrillage.osp_grillage.OspGrillage.set_member
    ospgrillage.osp_grillage.OspGrillage.analyze
    ospgrillage.osp_grillage.OspGrillage.get_results
    ospgrillage.osp_grillage.OspGrillage.get_nodes
    ospgrillage.osp_grillage.OspGrillage.get_element
    ospgrillage.osp_grillage.OspGrillage.clear_load_cases


Load module API
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The following methods can be called from the respective class objects of the Load module.

.. autosummary::
    :toctree: generated/


    ospgrillage.load.CompoundLoad.set_global_coord
    ospgrillage.load.CompoundLoad.add_load
    ospgrillage.load.LoadCase.add_load
    ospgrillage.load.MovingLoad.set_path
    ospgrillage.load.MovingLoad.add_load
    ospgrillage.load.MovingLoad.query


OspGrillage class
---------------------------

For information regarding the procedures in :class:`~OpsGrillage` class, see
:doc:`ModuleDoc`.

.. autoclass:: ospgrillage.osp_grillage.OspGrillage
    :members:
    :show-inheritance:

OspGrillageBeam class
^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: ospgrillage.osp_grillage.OspGrillageBeam
    :show-inheritance:
    :noindex:

OspGrillageShell class
^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: ospgrillage.osp_grillage.OspGrillageShell
    :show-inheritance:
    :noindex:

Analysis class
---------------------------

.. autoclass:: ospgrillage.osp_grillage.Analysis
    :members:
    :show-inheritance:


Result class
---------------------------
.. autoclass:: ospgrillage.osp_grillage.Results
    :members:
    :show-inheritance:



Material class
------------------------------------------

.. autoclass:: ospgrillage.material.Material
    :members:
    :show-inheritance:

Section class
------------------------------------------

.. autoclass:: ospgrillage.members.Section
    :members:
    :show-inheritance:

GrillageMember class
------------------------------------------

.. autoclass:: ospgrillage.members.GrillageMember
    :members:
    :show-inheritance:

Mesh class
------------------------------------------

.. autoclass:: ospgrillage.mesh.Mesh
    :members:
    :show-inheritance:

Load class
------------------------------------------
For information regarding definition of :class:`~Loads` class, see
:doc:`Loads`.

NodalLoad
^^^^^^^^^^^^^^^^

.. autoclass:: ospgrillage.load.NodalLoad
    :members:


PointLoad
^^^^^^^^^^^^^^^^

.. autoclass:: ospgrillage.load.PointLoad
    :show-inheritance:


LineLoading
^^^^^^^^^^^^^^^^

.. autoclass:: ospgrillage.load.LineLoading
    :show-inheritance:


PatchLoading
^^^^^^^^^^^^^^^^

.. autoclass:: ospgrillage.load.PatchLoading
    :show-inheritance:


CompoundLoad
------------------------------------------

.. autoclass:: ospgrillage.load.CompoundLoad
    :members:
    :show-inheritance:

MovingLoad
------------------------------------------

.. autoclass:: ospgrillage.load.MovingLoad
    :members:
    :show-inheritance:


LoadCase
------------------------------------------
For information regarding in :class:`~LoadCase` class, see
:doc:`Loads`.

.. autoclass:: ospgrillage.load.LoadCase
    :members:
    :show-inheritance:

Misc
------------------------------------------

Path for moving loads
^^^^^^^^^^^^^^^^^^^^^^^
.. autoclass:: ospgrillage.load.Path
    :members:
    :show-inheritance:

Envelope
^^^^^^^^^^^

.. autoclass:: ospgrillage.postprocessing.Envelope
    :members:


Shape functions
^^^^^^^^^^^^^^^^
.. autoclass:: ospgrillage.load.ShapeFunction
    :members:
    :show-inheritance: