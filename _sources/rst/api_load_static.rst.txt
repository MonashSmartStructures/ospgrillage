Static loads
============

These classes represent individual loads that are applied at specific
points, along lines, or over patches of the grillage model.

Factory functions
-----------------

.. autosummary::
   :toctree: generated/

   ~ospgrillage.load.create_load_vertex
   ~ospgrillage.load.create_load

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
