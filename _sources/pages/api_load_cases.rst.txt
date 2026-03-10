Load cases and models
=====================

These classes organise and combine individual :doc:`load types <api_load_types>`
into named analysis scenarios and reusable vehicle or load-pattern models.

- :class:`~ospgrillage.load.LoadCase` — a named scenario (e.g. "Dead Load",
  "Live Load") that collects loads for a single analysis run.
- :class:`~ospgrillage.load.CompoundLoad` — a spatial grouping of loads that
  move together as a unit (e.g. an axle arrangement).
- :class:`~ospgrillage.load.LoadModel` — a complete vehicle or load-pattern
  model composed of one or more compound loads, used as the payload for a
  :doc:`moving load <api_load_moving>`.

Factory functions
-----------------

.. autosummary::
   :toctree: generated/

   ~ospgrillage.load.create_load_case
   ~ospgrillage.load.create_compound_load
   ~ospgrillage.load.create_load_model

Class reference
---------------

LoadCase
~~~~~~~~

.. autoclass:: ospgrillage.load.LoadCase
   :members:
   :show-inheritance:

CompoundLoad
~~~~~~~~~~~~

.. autoclass:: ospgrillage.load.CompoundLoad
   :members:
   :show-inheritance:

LoadModel
~~~~~~~~~

.. autoclass:: ospgrillage.load.LoadModel
   :show-inheritance:
