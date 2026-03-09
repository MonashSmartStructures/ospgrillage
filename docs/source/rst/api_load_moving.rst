Moving loads
============

These classes define moving load models, the paths they travel along, and
the interpolation machinery used to distribute load to grillage nodes.

Factory functions
-----------------

.. autosummary::
   :toctree: generated/

   ~ospgrillage.load.create_moving_path
   ~ospgrillage.load.create_moving_load
   ~ospgrillage.load.create_load_model

Class methods
-------------

.. autosummary::
   :toctree: generated/

   ~ospgrillage.load.MovingLoad.set_path
   ~ospgrillage.load.MovingLoad.add_load
   ~ospgrillage.load.MovingLoad.query

Class reference
---------------

MovingLoad
~~~~~~~~~~

.. autoclass:: ospgrillage.load.MovingLoad
   :show-inheritance:

Path
~~~~

.. autoclass:: ospgrillage.load.Path
   :show-inheritance:

LoadModel
~~~~~~~~~

.. autoclass:: ospgrillage.load.LoadModel
   :show-inheritance:

ShapeFunction
~~~~~~~~~~~~~

.. autoclass:: ospgrillage.load.ShapeFunction
   :show-inheritance:
