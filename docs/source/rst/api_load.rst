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

NodalLoad
~~~~~~~~~

.. autoclass:: ospgrillage.load.NodalLoad
   :show-inheritance:

PointLoad
~~~~~~~~~

.. autoclass:: ospgrillage.load.PointLoad
   :show-inheritance:

LineLoading
~~~~~~~~~~~

.. autoclass:: ospgrillage.load.LineLoading
   :show-inheritance:

PatchLoading
~~~~~~~~~~~~

.. autoclass:: ospgrillage.load.PatchLoading
   :show-inheritance:

CompoundLoad
~~~~~~~~~~~~

.. autoclass:: ospgrillage.load.CompoundLoad
   :show-inheritance:

MovingLoad
~~~~~~~~~~

.. autoclass:: ospgrillage.load.MovingLoad
   :show-inheritance:

LoadCase
~~~~~~~~

.. autoclass:: ospgrillage.load.LoadCase
   :show-inheritance:

LoadModel
~~~~~~~~~

.. autoclass:: ospgrillage.load.LoadModel
   :show-inheritance:

Path
~~~~

.. autoclass:: ospgrillage.load.Path
   :show-inheritance:

ShapeFunction
~~~~~~~~~~~~~

.. autoclass:: ospgrillage.load.ShapeFunction
   :show-inheritance:
