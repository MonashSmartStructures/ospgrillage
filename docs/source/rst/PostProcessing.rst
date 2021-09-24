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
Load envelope is generated from load combination results for extrema of load effect using `get_envelope()` function. Envelope are
chosen based on user selected component (*array* keyword) as either "displacements" or "forces", extrema as either maximum or minimum,
and load effect component (e.g. "dy" for displacements). The `get_envelope()` function is defined as follows:

.. code-block:: python
    first_combination = comb_results[0] # list of combination xarray, get the first
    envelope = og.get_envelope(ds=first_combination,load_effect="dy",array="displacements") # creates the envelope obj
    disp_env = envelope.get() # get the output xarray of envelope


Plotting results
--------------------------------------

Current limitation of plotting module
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

`OpenSeesPy`'s visualization module `ops_vis` offers comprehensive visualization of analysis results.
However, `ops_vis`'s plotting operates only for the current model (and analysis) instance in `OpenSees`
framework. In other words multiple plots of different analysis results is not straightforward for `ops_vis`.
Additionally, `ops_vis` does not contain enveloping feature across multiple analysis - especially for moving
load analysis comprise of multiple incremental load case for each moving load position.

In the following section, we present an alternative way to visualize results of *ospgrillage* - template codes to plot and visualize results.

Suggested method using matplotlib
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Here are some template codes for plotting load effects using Python's `matplotlib` library tools.

For displacement components:

.. code-block:: python

    # get all node information
    nodes = example_bridge.get_nodes() # dictionary containing information of nodes
    # extract list of x and z coordinate of nodes
    x_coord = [spec['coordinate'][0] for spec in nodes.values()]
    z_coord = [spec['coordinate'][2] for spec in nodes.values()]

    # get displacement load effect - specifically dy
    load_effect = result.displacements.sel(Component="dy")[0] # a list of array, therefore access element 0
    ax = og.plt.axes(projection='3d') # create plot
    ax.scatter(x_coord,z_coord,load_effect) # plot load effect against x and z coordinate positions

For forces components of beam elements:

.. code-block:: python

    # template code to plot load effect - herein plot "Mz" global of exterior main beam 2
    nodes=bridge_28.get_nodes()
    nodes_to_plot = bridge_28.get_element(member="exterior_main_beam_2", options="nodes",z_group_num=0)
    eletag = bridge_28.get_element(member="exterior_main_beam_2", options="elements")
    load_effect_i = results.forces.sel(Component="Mz_i",Element=eletag)[0]
    load_effect_j = results.forces.sel(Component="Mz_j",Element=eletag)[0]
    load_effect = og.np.concatenate(([load_effect_i[0].values],load_effect_j.values))
    results.ele_nodes.sel(Element=eletag, Nodes='i')
    node_x = [nodes[n]['coordinate'][0] for n in nodes_to_plot[0]]
    node_z = [nodes[n]['coordinate'][2] for n in nodes_to_plot[0]]
    ax = og.plt.axes(projection='3d')
    ax.plot(node_x,node_z,load_effect)

For force component version 2:

.. code-block:: python

    for ele in eletag:
    ele_components = results.forces.sel(Element=ele, Component=["Vx_i", "Vy_i", "Vz_i", "Mx_i", "My_i", "Mz_i", "Vx_j", "Vy_j", "Vz_j", "Mx_j", "My_j",
                       "Mz_j"])[0].values
    #ele_components = results.forces.sel(Element=ele)[0].values[:12]
    ele_node = results.ele_nodes.sel(Element=ele)
    xx = [nodes[n]['coordinate'][0] for n in ele_node.values]
    yy = [nodes[n]['coordinate'][1] for n in ele_node.values]
    zz = [nodes[n]['coordinate'][2] for n in ele_node.values]
    s,al = og.opsv.section_force_distribution_3d(ex=xx,ey=yy,ez=zz,pl=ele_components)
    ax.plot(xx,zz,s[:,5])

