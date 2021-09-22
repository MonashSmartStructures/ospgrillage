========================
Post Processing
========================

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

The dataset contains two dataarrays representing load effects:

*. displacements i.e. rotation and translations
*. forces e.g. Bending about z axis, Shear forces etc.

To extract displacements, access the "displacements" data array of results

.. code-block:: python

    result.displacements.sel(Component="dy")


Getting combinations
--------------------------------------




Plotting results
--------------------------------------

Using ops_vis
^^^^^^^^^^^^^

Using matplotlib
^^^^^^^^^^^^^^^^^

The following code block outlines a method to plot results of data array.

For displacement

.. code-block:: python

    # get node information
    nodes = example_bridge.get_nodes() # ospgrillage way to store node information

    x_coord = [spec['coordinate'][0] for spec in nodes.values()]
    z_coord = [spec['coordinate'][2] for spec in nodes.values()]

    # get load effect
    load_effect = result.displacements.sel(Component="dy")[0]
    ax = og.plt.axes(projection='3d')
    ax.scatter(x_coord,z_coord,load_effect)

For forces.

.. code-block:: python
