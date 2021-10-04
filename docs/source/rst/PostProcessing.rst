========================
Getting Results
========================

For all example code in this page, *ospgrillage* is imported as ``ospg``

.. code-block:: python
    import ospgrillage as ospg

Extracting results
--------------------------------------

After analysis, results are obtained using :func:`~ospgrillage.OspGrillage.get_results` function.
The following example extracts results for all defined analysis.

.. code-block:: python
    result = example_bridge.get_results() # this extracts all results
    result = example_bridge.get_results(load_case = "patch load case") # this extracts only the patch load case results

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

    disp_array = result.displacements # displacement components
    force_array = result.forces # force components

A third variable present in the DataSet of Figure 1 is the variable for element and its respective nodes.

Accessing and querying data
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

From the data arrays, users can access various component in each load effect using `xarray`'s data array commands.
Following example extracts the displacment 'dy' component using `xarray`'s `sel()` function.

.. code-block:: python
    disp_array.sel(Component='dy') # vertical deflection
    force_array.sel(Component='Mz_i')

The following components


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
    envelope = ospg.get_envelope(ds=first_combination,load_effect="dy",array="displacements") # creates the envelope obj
    disp_env = envelope.get() # step to get envelope of xarray



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



Plotting results from DataArrays
--------------------------------------

Current limitation of plotting module
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

`OpenSeesPy`'s visualization module `ops_vis` offers comprehensive visualization analysis results in `OpenSees`.
However, `ops_vis`'s plotting operates only for the current model (and analysis) instance in `OpenSees`
framework. In other words multiple plots of different analysis results is not straightforward for `ops_vis`.
Additionally, `ops_vis` does not contain enveloping feature across multiple analysis - especially for moving
load analysis comprise of multiple incremental load case for each moving load position. Overall, `ops_vis` is unable to plot
results from `xarray` data set

The following code example allow users to plot results from **current analysis**
using `ops_vis`:

.. code-block:: python

    ospg.opsv.section_force_diagram_3d('Mz', {}, 1) # here change name string argument to force component of interest


.. note::

    `opsv` gives the correct result only if the load case of interest is the only load case
    being :func:`~ospgrillage.osp_grillage.OspGrillage.analyze`.


In the following section, we present an alternative way to visualize results from the `xarray` DataSets.

Template code for plotting results
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
For users wishing to plot results from `xarray` DataSets, here are some template codes for plotting load effects using Python's `matplotlib` library tools.

Scatter plot of "dy" component in each node of ``example_bridge``:

.. code-block:: python

    # get all node information
    nodes = example_bridge.get_nodes() # dictionary containing information of nodes
    # extract list of x and z coordinate of nodes
    x_coord = [spec['coordinate'][0] for spec in nodes.values()]
    z_coord = [spec['coordinate'][2] for spec in nodes.values()]

    # get displacement load effect - vertical "dy"
    load_effect = result.displacements.sel(Component="dy")[0] # Modify component here accordingly
    ax = og.plt.axes(projection='3d') # create plot
    ax.scatter(x_coord,z_coord,load_effect) # plot load effect against x and z coordinate positions


..  figure:: ../../_images/example_deflected.PNG
    :align: center
    :scale: 75 %

    Figure 1: Structure of DataSet.

Plotting "Mz" of "exterior_main_beam_2" in ``example_bridge`` model:

.. code-block:: python

    # template code to plot load effect - herein plot "Mz" global of exterior main beam 2
    ax = ospg.plt.axes(projection='3d') # create plot window
    nodes=example_bridge.get_nodes() # extract node information of model
    nodes_to_plot = example_bridge.get_element(member="exterior_main_beam_2", options="nodes",z_group_num=0) # extract nodes of exterior beam
    eletag = example_bridge.get_element(member="exterior_main_beam_2", options="elements") #
    load_effect_i = results.forces.sel(Component="Mz_i",Element=eletag)[0]
    load_effect_j = results.forces.sel(Component="Mz_j",Element=eletag)[0]
    load_effect = ospg.np.concatenate(([load_effect_i[0].values],load_effect_j.values))
    results.ele_nodes.sel(Element=eletag, Nodes='i')
    node_x = [nodes[n]['coordinate'][0] for n in nodes_to_plot[0]]
    node_z = [nodes[n]['coordinate'][2] for n in nodes_to_plot[0]]
    ax = ospg.plt.axes(projection='3d')
    ax.plot(node_x,node_z,load_effect)


Plotting "Mz" of "exterior_main_beam_2" in ``example_bridge``- version 2 leveraging function of `ops_vis` module:

.. code-block:: python

    ax = ospg.plt.axes(projection='3d') # create plot window
    nodes=example_bridge.get_nodes() # extract node information of model
    eletag = example_bridge.get_element(member="exterior_main_beam_2", options="elements") # get ele tag of grillage elements
    # loop ele tags of ele
    for ele in eletag:
        # get force components
        ele_components = results.forces.sel(Element=ele, Component=["Vx_i", "Vy_i", "Vz_i", "Mx_i", "My_i", "Mz_i", "Vx_j", "Vy_j", "Vz_j", "Mx_j", "My_j",
                           "Mz_j"])[0].values
        # get nodes of ele
        ele_node = results.ele_nodes.sel(Element=ele)
        # create arrays for x y and z for plots
        xx = [nodes[n]['coordinate'][0] for n in ele_node.values]
        yy = [nodes[n]['coordinate'][1] for n in ele_node.values]
        zz = [nodes[n]['coordinate'][2] for n in ele_node.values]
        # use ops_vis module to get force distribution on element
        s,al = ospg.opsv.section_force_distribution_3d(ex=xx,ey=yy,ez=zz,pl=ele_components)
        # plot desire element force component
        ax.plot(xx,zz,s[:,5]) # Here change int accordingly: {0:Fx,1:Fy,2:Fz,3:Mx,4:My,5:Mz}

..  figure:: ../../_images/example_bmd.PNG
    :align: center
    :scale: 75 %

    Figure 2: Bending moment about z axis of exterior main beam 2 .