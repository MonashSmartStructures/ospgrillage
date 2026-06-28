Analysis and results
====================

Running the analysis and extracting results.

For influence analyses, `shape_function="hermite"` denotes the higher-order
load-distribution path used by *ospgrillage*: the existing Hermite
quadrilateral distributor is used in four-node regions, while three-node skew
regions use the DKT-style condensed triangular distributor.

For skewed/curved bridges, influence-line station abscissa
(``load_coord="station"``) and influence-surface station axes
(``longitudinal_station``, ``transverse_station``) provide geometry-robust
reduction coordinates independent of global Cartesian layout.

OspGrillage methods
-------------------

.. autosummary::
   :toctree: generated/

   ~ospgrillage.osp_grillage.OspGrillage.analyze
   ~ospgrillage.osp_grillage.OspGrillage.analyze_influence_lines
   ~ospgrillage.osp_grillage.OspGrillage.analyze_influence_surfaces
   ~ospgrillage.osp_grillage.OspGrillage.analyze_il
   ~ospgrillage.osp_grillage.OspGrillage.analyze_is
   ~ospgrillage.osp_grillage.OspGrillage.analyze_influence_line
   ~ospgrillage.osp_grillage.OspGrillage.analyze_influence_surface
   ~ospgrillage.osp_grillage.OspGrillage.get_il
   ~ospgrillage.osp_grillage.OspGrillage.get_is
   ~ospgrillage.osp_grillage.OspGrillage.get_results
   ~ospgrillage.osp_grillage.OspGrillage.get_influence_results
   ~ospgrillage.osp_grillage.OspGrillage.plot_il
   ~ospgrillage.osp_grillage.OspGrillage.plot_is
   ~ospgrillage.osp_grillage.OspGrillage.export_il
   ~ospgrillage.osp_grillage.OspGrillage.export_is

Class reference
---------------

Analysis
~~~~~~~~

.. autoclass:: ospgrillage.osp_grillage.Analysis
   :show-inheritance:

Results
~~~~~~~

.. autoclass:: ospgrillage.osp_grillage.Results
   :show-inheritance:

InfluenceResultSet
~~~~~~~~~~~~~~~~~~

.. autoclass:: ospgrillage.osp_grillage.InfluenceResultSet
   :show-inheritance:

InfluenceLineResults
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: ospgrillage.osp_grillage.InfluenceLineResults
   :show-inheritance:

   Includes ``plot()``, ``save()/to_netcdf()``, and ``to_csv()`` helpers.

InfluenceSurfaceResults
~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: ospgrillage.osp_grillage.InfluenceSurfaceResults
   :show-inheritance:

   Includes ``plot()``, ``save()/to_netcdf()``, and ``to_csv()`` helpers.
