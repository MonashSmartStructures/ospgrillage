Moving loads
============

These classes define the machinery for moving-load analysis: the load travels
along a :class:`~ospgrillage.load.Path` and the
:class:`~ospgrillage.load.MovingLoad` engine distributes the payload
(a :class:`~ospgrillage.load.LoadModel` from
:doc:`load cases and models <api_load_cases>`) to grillage nodes at each
position increment.

Factory functions
-----------------

.. autosummary::
   :toctree: generated/

   ~ospgrillage.load.create_moving_load
   ~ospgrillage.load.create_moving_path

Class methods
-------------

.. autosummary::
   :toctree: generated/

   ~ospgrillage.load.MovingLoad.set_path
   ~ospgrillage.load.MovingLoad.add_load
   ~ospgrillage.load.MovingLoad.query
   ~ospgrillage.load.MovingLoad.parse_moving_load_cases

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
