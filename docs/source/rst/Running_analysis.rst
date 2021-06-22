========================
Analyzing the grillage model
========================

The *ops-grillage* module allows users to define loads and load combinations. In addition, defining moving load analysis
is also available to run a moving load analysis.

Defining loads
------------------------
Loads are defined using Point, Line, and Patch loads. Each point load is defined as a class object. Each class requires
user to specify its load point - a namedTuple LoadPoint(x,y,z,p) where x,y,z are the coordinates of the load point, and
p is the magnitude of the vertical loading.

Depending on the load type, each load type takes in variety of Load points. Point load takes in a single LoadPoint.
Line load takes in at least two points. Patch load takes it at least four points.

Defining point loads

.. code-block:: python

    location = LoadPoint(5, 0, 2, 20)  # create load point
    Single = PointLoad(name="single point", point1=location)


Defining Line Loads

.. code-block:: python

    barrierpoint_1 = LoadPoint(-1, 0, 3, 2)
    barrierpoint_2 = LoadPoint(11, 0, 3, 2)
    Barrier = LineLoading("Barrier curb load", point1=barrierpoint_1, point2=barrierpoint_2)

Defining Patch loads

.. code-block:: python

    lane_point_1 = LoadPoint(0, 0, 3, 5)
    lane_point_2 = LoadPoint(8, 0, 3, 5)
    lane_point_3 = LoadPoint(8, 0, 5, 5)
    lane_point_4 = LoadPoint(0, 0, 5, 5)
    Lane = PatchLoading("Lane 1", point1=lane_point_1, point2=lane_point_2, point3=lane_point_3, point4=lane_point_4)


Defining load combination
------------------------



Defining moving loads
------------------------


Running the analysis
------------------------



Viewing results
------------------------

A set of plotting functions are included as part of the `op-grillage` module - the `PlotWizard` command. To draw and
plot components of the model, users run the following example. In the example, the plot_section() function draws and
plots the longitudinal members of the grillage.

.. code-block:: python

    import PlotWizard
    plot_section(test_bridge, "interior_main_beam", 'r')

The `plot_section()` function is based on matplotlib plotting commands.

Alternatively, result visualization can be achieved using the Openseespy module - ops_vis. The `ops_vis` module is one
of the post-processing modules of Openseespy. The `ops-vis` module has gone through numerous updates and has reach
maturity for many post-processing applications. This is the recommended plotting feature at the current version of
`op-grillage`.

For example users can view the model using the `model()` command. To do this, users add the following command and the
end of the output py file.

.. code-block:: python

    ops.model()
