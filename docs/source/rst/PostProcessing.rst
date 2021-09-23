========================
Post-Processing
========================

This page shows the post-processing capabilities of *ospgrillage*. Examples herein should guide users to extract desired results
from analysis.


Getting results
--------------------------------------

After analysis, results are obtained using `get_results()` function. The following example code demonstrates
the `get_results()` utility.

.. code-block:: python
    result = example_bridge.get_results() # this extracts all results
    result = example_bridge.get_results(load_case = "patch load case") # this extracts only the patch load case results

The **result** variable is a `Xarray` data set.

Structure of data sets
--------------------------------------

The dataset contains two main data arrays representing load effects:

*. displacements i.e. rotation and translations
*. forces e.g. Bending about z axis, Shear forces etc.

Following example shows how each data array of results is accessed :

.. code-block:: python

    disp_array = result.displacements
    force_array = result.forces

Users can access specific component in each load effect data array. Following example extracts the displacment 'dy' component using `Xarray`'s
`sel()` function.

.. code-block:: python
    disp_array.sel(Component='dy') # vertical deflection
    force_array.sel(Component='Mz_i')


Getting combinations
--------------------------------------
Load combinations are computed on the fly in `get_results()` by specifying a keyword argument for combinations.
Argument takes in a `dict` having load case name strings as key, and corresponding load factor as value. The following
example code define a load combinations having two load cases.

.. code-block:: python

    comb_result = example_bridge.get_results(combinations={"patch_load_case":2,"moving_truck":1.6})

Load envelope
--------------------------------------
Load envelope is generated from load combination results for extrema of load effect as a new xarray.

.. code-block:: python
    first_combination = comb_results[0]
    envelope = og.get_envelope(ds=first_combination,load_effect="dy",array="displacements")
    disp_env = envelope.get()





Plotting results
--------------------------------------

Current limitation of plotting module
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

`OpenSeesPy`'s visualization module `ops_vis` offers users the capability to visualize analysis results on a model in
comprehensive ways. However, `ops_vis` operates on plotting results of the current model (and analysis) instance in `OpenSees`
framework. Additionally, `ops_vis` does not contain enveloping feature across multiple analysis - this especially the case for moving
load analysis.

In the following section, we will present an alternative way to visualize results of *ospgrillage* - albeit in pythonic code lines.

Suggested method using matplotlib
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Here are some example code which can help plot desired load effects.

For displacement array:

.. code-block:: python

    # template code to plot displacements
    # get all node information
    nodes = example_bridge.get_nodes() # dictionary containing information of nodes
    # extract list of x and z coordinate of nodes
    x_coord = [spec['coordinate'][0] for spec in nodes.values()]
    z_coord = [spec['coordinate'][2] for spec in nodes.values()]

    # get load effect
    load_effect = result.displacements.sel(Component="dy")[0] # Alter the component according to user
    ax = og.plt.axes(projection='3d') # create plot
    ax.scatter(x_coord,z_coord,load_effect) # plot load effect against x and z coordinate positions

For forces.

.. code-block:: python

    # template code to plot load effect - herein plot "Mz" global of exterior main beam 2
    nodes=bridge_28.get_nodes()
    nodes_to_plot = bridge_28.get_element(member="exterior_main_beam_2", options="nodes")
    eletag = bridge_28.get_element(member="exterior_main_beam_2", options="elements")
    load_effect_i = results.forces.sel(Component="Mz_i",Element=eletag)[0]
    load_effect_j = results.forces.sel(Component="Mz_j",Element=eletag)[0]
    load_effect = og.np.concatenate(([load_effect_i[0].values],load_effect_j.values))
    results.ele_nodes.sel(Element=eletag, Nodes='i')
    node_x = [nodes[n]['coordinate'][0] for n in nodes_to_plot[0]]
    node_z = [nodes[n]['coordinate'][2] for n in nodes_to_plot[0]]
    ax = og.plt.axes(projection='3d')
    ax.plot(node_x,node_z,load_effect)

plot for interior beams

