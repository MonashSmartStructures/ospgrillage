========================
Getting Results
========================

For all example code in this page, *ospgrillage* is imported as ``og``

.. code-block:: python
    import ospgrillage as og

Extracting results
--------------------------------------

After analysis, results are obtained using :func:`~ospgrillage.osp_grillage.OspGrillage.get_results` function.
The following example extracts results for all defined analysis of ``example_bridge``.

.. code-block:: python

    all_result = example_bridge.get_results() # this extracts all results
    patch_result = example_bridge.get_results(load_case = "patch load case") # this extracts only the patch load case results

The returned **result** variable is an
`xarray DataSet <http://xarray.pydata.org/en/stable/generated/xarray.Dataset.html>`_.

Structure of xarray DataSet
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Figure 1 shows the structure of the xarray DataSet for results.
The dataset contains two `xarray DataArray <http://xarray.pydata.org/en/stable/generated/xarray.DataArray.html#xarray.DataArray>`_.
that represent two groups of load effects:

#. **displacements** i.e. rotation and translations
#. **forces** e.g. bending about z axis, Shear forces etc.

..  figure:: ../../_images/structure_dataset.PNG
    :align: center
    :scale: 75 %

    Figure 1: Structure of DataSet.

Depending on the model type, the DataArray for **forces** is grouped according to element types. For example
the :ref:`shell hybrid model` with beam and shell elements have forces recorded in **forces_beam** and **forces_shell**
respectively (Figure 1). When this is the case, **ele_nodes** will be split into **ele_nodes_beam** and **ele_nodes_shell**
as well.

Following example shows how each DataArray is accessed from **result** DataSet:

.. code-block:: python

    disp_array = all_result.displacements # displacement components
    force_array = all_result.forces # force components

A third variable present in the DataSet of Figure 1 is the variable for element and its respective nodes.

Accessing and querying data
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

From the data arrays, users can access various component in each load effect using `xarray`'s data array commands.

Following example extracts the displacment 'dy' component using `xarray`'s ``sel()`` function.

.. code-block:: python

    disp_array.sel(Component='dy') # select data of "dy"
    force_array.sel(Component='Mz_i') # select data of "Mz_i"

Following example shows how to extract results for specific load cases with specific element/node:

.. code-block:: python

    disp_array.sel(Loadcase="patch load case",Node=20)
    force_array.sel(Loadcase="Barrier", Element=[2,3,4])

Getting combinations
--------------------------------------
Load combinations are computed on the fly in `get_results()` by specifying a keyword argument for combinations.
Argument takes in a `dict` having load case name strings as key, and corresponding load factor as value. The following
example code define a load combinations having two load cases.

.. code-block:: python

    comb_result = example_bridge.get_results(combinations={"patch_load_case":2,"moving_truck":1.6})

Getting load envelope
--------------------------------------
Load envelope is generated from load combination results for extrema of load effect using :func:`~ospgrillage.static.create_envelope` function.
Envelope are chosen based on user selected component (*array* keyword) as either "displacements" or "forces", extrema as either maximum or minimum,
and load effect component (e.g. "dy" for displacements). The `get_envelope()` function is defined as follows:

.. code-block:: python

    first_combination = comb_results[0] # list of combination xarray, get the first
    envelope = og.get_envelope(ds=first_combination,load_effect="dy",array="displacements") # creates the envelope obj
    disp_env = envelope.get() # output the created envelope of xarray


Getting specific properties of model
--------------------------------------

Node
^^^^^^^^^^^^^^^^^^^

.. automethod:: ospgrillage.OspGrillage.get_nodes()
    :noindex:

Element
^^^^^^^^^^^^^^^^^^^

.. automethod:: ospgrillage.OspGrillage.get_element()
    :noindex:



Plotting results of DataArrays
--------------------------------------

Current limitation of `OpenSees` visualization module
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

`OpenSeesPy`'s visualization module - `ops_vis` - offers comprehensive visualization analysis results in `OpenSees`.
However, `ops_vis` operates only for a single model instance (and analysis) in `OpenSees`
framework. In other words, results from xarray DataSet (of :func:`~ospgrillage.osp_grillage.OspGrillage.get_results)
cannot be plotted using the current visualization module.
Additionally, `ops_vis` does not contain enveloping feature across multiple analysis - especially for moving
load analysis comprise of multiple incremental load case for each moving load position.

If needed, users can still utilize `ops_vis` however only in a specific condition i.e. only a single load case is defined
and :func:`~ospgrillage.osp_grillage.OspGrillage.analyze` in the `OpenSees` framework.
With only a single load case and analysis, users can directly access the model results
and plot using `ops_vis`. The following code example plots the results of the **current analysis instance **
using `ops_vis`:

.. code-block:: python

    og.opsv.section_force_diagram_3d('Mz', {}, 1) # here change name string argument to force component of interest


.. note::

    `opsv` only works for model template 1 (beam grillage) and 2 (beam grillage with rigid links). Plotting of shell model
    type is not supported as of *ospgrillage* version 0.1.0


*ospgrillage* post-processing module
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
For users wishing to plot results from xarray DataSet (multiple analysis),
*ospgrillage* contains a dedicated post-processing module as of version 0.1.0 to visualize these results.

.. note::

    The plotting functions of post-processing module is at alpha development stage as compared to other modules. As of version 0.1.0,
    it is sufficient to plot components from the xarray DataSets.

Plotting functions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For this section, we will refer to an exemplar 28 m super-T bridge (Figure 1). The bridge grillage has been created
and its :class:`~ospgrillage.osp_grillage.OspGrillage` object is defined as ``bridge_28``.

..  figure:: ../../_images/28m_bridge.png
    :align: center
    :scale: 25 %

    Figure 1: 28 m super-T bridge model.


To plot deflection components from ``displacement`` DataArray, use :func:`~ospgrillage.postprocessing.plot_defo`. To use this function
users need to specify the specific grillage member - this function returns a 2-D plot of displacement diagram.
Following example plots the vertical deflection of ``bridge_28``, for "exterior_main_beam_2" member - plot shown in
Figure 2:

.. code-block:: python

    og.plot_defo(bridge_28, results, member="exterior_main_beam_2", option= "nodes")

..  figure:: ../../_images/example_deflected.PNG
    :align: center
    :scale: 25 %

    Figure 2: Deflected shape of of exterior main beam 2.


To plot force components from ``forces`` DataArray, use :func:`~ospgrillage.postprocessing.plot_force`. Similar to
:func:`~ospgrillage.postprocessing.plot_defo`, users need to specify name string of specific grillage member.
Following example plots the bending moment "Mz" of "exterior_main_beam_2" in ``bridge_28`` - plot shown in Figure 3:

.. code-block:: python

    og.plot_force(bridge_28, results, member="exterior_main_beam_2", component="Mz")

..  figure:: ../../_images/example_bmd.PNG
    :align: center
    :scale: 25 %

    Figure 3: Bending moment about z axis of exterior main beam 2 .