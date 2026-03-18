Load types
==========

These classes represent individual loads applied at specific points, along
lines, or over patches of the grillage model. They are the basic building
blocks that are assembled into :doc:`load cases and models <api_load_cases>`.

Data types
----------

.. class:: ospgrillage.load.LoadVertex(x, y, z, p)

   A ``namedtuple`` giving a spatial coordinate and load magnitude — the
   building block of all load types.

   :param x: x coordinate.
   :param y: y coordinate (usually ``0`` for grillage models).
   :param z: z coordinate.
   :param p: Load magnitude (force, force/length, or force/area).

   .. versionadded:: 0.5.0

.. data:: ospgrillage.load.LoadPoint

   Deprecated alias for :class:`LoadVertex`.  Existing code using
   ``LoadPoint`` will continue to work, but new code should use
   ``LoadVertex``.

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
