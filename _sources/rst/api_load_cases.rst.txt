Load cases
==========

These classes are used to assemble individual loads into named load cases
and compound (grouped) loads that can be applied to the model together.

Factory functions
-----------------

.. autosummary::
   :toctree: generated/

   ~ospgrillage.load.create_load_case
   ~ospgrillage.load.create_compound_load

Class methods
-------------

.. autosummary::
   :toctree: generated/

   ~ospgrillage.load.CompoundLoad.set_global_coord
   ~ospgrillage.load.CompoundLoad.add_load
   ~ospgrillage.load.LoadCase.add_load

Class reference
---------------

LoadCase
~~~~~~~~

.. autoclass:: ospgrillage.load.LoadCase
   :show-inheritance:

CompoundLoad
~~~~~~~~~~~~

.. autoclass:: ospgrillage.load.CompoundLoad
   :show-inheritance:
