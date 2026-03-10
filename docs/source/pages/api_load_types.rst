Load types
==========

These classes represent individual loads applied at specific points, along
lines, or over patches of the grillage model. They are the basic building
blocks that are assembled into :doc:`load cases and models <api_load_cases>`.

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
