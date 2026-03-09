Load module
===========

Factory functions
-----------------

.. autosummary::
   :toctree: generated/

   ~ospgrillage.load.create_load_vertex
   ~ospgrillage.load.create_load
   ~ospgrillage.load.create_load_case
   ~ospgrillage.load.create_compound_load
   ~ospgrillage.load.create_moving_path
   ~ospgrillage.load.create_moving_load
   ~ospgrillage.load.create_load_model

Class methods
-------------

.. autosummary::
   :toctree: generated/

   ~ospgrillage.load.CompoundLoad.set_global_coord
   ~ospgrillage.load.CompoundLoad.add_load
   ~ospgrillage.load.LoadCase.add_load
   ~ospgrillage.load.MovingLoad.set_path
   ~ospgrillage.load.MovingLoad.add_load
   ~ospgrillage.load.MovingLoad.query

Class reference
---------------

.. autoclass:: ospgrillage.load.NodalLoad
   :members:
   :show-inheritance:

.. autoclass:: ospgrillage.load.PointLoad
   :members:
   :show-inheritance:

.. autoclass:: ospgrillage.load.LineLoading
   :members:
   :show-inheritance:

.. autoclass:: ospgrillage.load.PatchLoading
   :members:
   :show-inheritance:

.. autoclass:: ospgrillage.load.CompoundLoad
   :members:
   :show-inheritance:

.. autoclass:: ospgrillage.load.MovingLoad
   :members:
   :show-inheritance:

.. autoclass:: ospgrillage.load.LoadCase
   :members:
   :show-inheritance:

.. autoclass:: ospgrillage.load.LoadModel
   :members:
   :show-inheritance:

.. autoclass:: ospgrillage.load.Path
   :members:
   :show-inheritance:

.. autoclass:: ospgrillage.load.ShapeFunction
   :members:
   :show-inheritance:
