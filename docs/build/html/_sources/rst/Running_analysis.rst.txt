========================
Performing analysis
========================

Having created the grillage model, users can proceed with grillage analysis. The *ops-grillage* module allows grillage analysis utilities
by allowing users to specify load cases and run load case analysis. Furthermore, *ops-grillage* module also options for moving load analysis.


Defining loads
------------------------
Loads are defined using `Point`_, `Line`_, and `Patch`_ loads. Each point load is defined as a class object. Each load type requires
user to specify its load point - a namedTuple LoadPoint(x,y,z,p) where x,y,z are the coordinates of the load point, and
p is the magnitude of the vertical loading.

Depending on the load type, different number of load points are needed for various load type. For example, Point load takes in a single LoadPoint tuple;
Line load takes in at least two LoadPoint tuple (corresponds to the start and end of the line load); and Patch load takes it at least four points
(corresponds to the vertices of the patch load).

Here are few examples of creating load types. Each load type takes in variable number of LoadPoint tuple as shown below:

Point Loads

.. _Point:

.. code-block:: python

    point_load_location = LoadPoint(5, 0, 2, 20)  # create load point
    single_point_load = PointLoad(name="single point", point1=location)


.. _Line:

Line Loads

.. code-block:: python

    barrier_point_1 = LoadPoint(-1, 0, 3, 2)
    barrier_point_2 = LoadPoint(11, 0, 3, 2)
    Barrier = LineLoading("Barrier curb load", point1=barrier_point_1, point2=barrier_point_2)

.. _Patch:

Patch loads

.. code-block:: python

    lane_point_1 = LoadPoint(0, 0, 3, 5)
    lane_point_2 = LoadPoint(8, 0, 3, 5)
    lane_point_3 = LoadPoint(8, 0, 5, 5)
    lane_point_4 = LoadPoint(0, 0, 5, 5)
    Lane = PatchLoading("Lane 1", point1=lane_point_1, point2=lane_point_2, point3=lane_point_3, point4=lane_point_4)

.. note::

    Each load object (Point, Line, Patch) have the option to be defined as local coordinate or global (with respect to
    coordinate system of the created grillage model

.. _load cases:

Load cases
______________________
Load cases are a set of loads used to define a particular loading condition.

After load objects are created, users add the load objects to :class:`LoadCase` class objects. First, users create a
:class:`LoadCase` class object and giving it its name.

.. code-block:: python

    ULS_DL = LoadCase(name="ULS-DL")

Users then pass load objects as input parameters using ``add_load_groups()`` function.

.. code-block:: python

    ULS_DL.add_load_groups(Single)  # each line adds individual load types to the load case
    ULS_DL.add_load_groups(Barrier)
    ULS_DL.add_load_groups(Lane)

After adding loads, the ``ULS_DL`` object can be added to grillage model for analysis using the ``add_load_case()``
function of :class:`OpsGrillage` class. Users repeat this step for any defined load cases.

.. code-block:: python

    example_bridge.add_load_case(ULS_DL)  # adding this load case to grillage model


To analyse loadcase(s), users run the class function ``analyse_load_case()``. This will analyse all load
cases added to the grillage model previously.

.. code-block:: python

    example_bridge.analyse_load_case()


Compound loads
__________________________
Two or more groups of load objects can be compounded into a compound load. Compound loads are treated as a single load group within a load case
having same reference points (e.g. tandem axle) and properties (e.g. load factor)

To create a compound load, use the :class:`CompoundLoad` class - passing load objects for compounding as input parameters.

The following code creates and add a point and line load to the :class:`CompoundLoad` object.

.. code-block:: python

    # compound load
    M1600 = CompoundLoad("Lane and Barrier") # lane and barrier compounded
    M1600.add_load(load_obj=Single, local_coord=Point(5,0,5))
    M1600.add_load(load_obj=Barrier, local_coord=Point(3,0,5))
    M1600.set_global_coord(Point(4,0,3))

From this point, the compound loads are added into `load cases`_ as per ``add_load_groups()`` function.


Defining moving loads
------------------------
For moving load analysis, users create moving load objects using :class:`Moving Load` class. The moving load class takes a Load object and moves the load
through a path described by a :class:`Path` object. Path are defined using two Point(x,y,z) namedtuple to describe its start and end position.

.. code-block:: python

    single_path = Path(start_point=Point(2,0,2), end_point= Point(4,0,3))  # create path object
    move_point = MovingLoad(name="single_moving_point")
    move_point.add_loads(load_obj=front_wheel,path_obj=single_path.get_path_points())

After adding all loads and respective paths, users run the class function ``parse_moving_load_case()`` which instructs the class to create multiple `load cases`_ for
which corresponds to the load condition as the load moves through each increment of the path.

.. code-block:: python

    move_point.parse_moving_load_cases() # step to finalise moving load - creates incremental load cases for each position of the moving load

From here, use the ``add_moving_load_case()`` function of the :class:`OpsGrillage` to add the moving load as a moving load case. Similar to `load cases`_, user run ``analyse_moving_load_case()``
to analyze the moving load case.

.. code-block:: python

    example_bridge.add_moving_load_case(move_point)
    example_bridge.analyse_moving_load_case()


Defining load combination
------------------------
Load combinations analysis are performed by using the :class:`OpsGrillage` function ``add_load_combination()`` function.
Load combinations are defined by passing an input dictionary of basic load case name as keys with load factors as
values. An example dictionary is shown as follows:

.. code-block:: python

    load_combinations = {'ULS-DL':1.2,'Live traffic':1.7}
    example_bridge.add_load_combination(name = "ULS", input_dict = load_combinations )

Getting results
------------------------
Results are returned as `data arrays <http://xarray.pydata.org/en/stable/user-guide/data-structures.html#>`_ (python's Xarray module).
To get results, run the ``get_results()`` function and two outputs will be returned:

.. code-block:: python

    basic_load_case_result,moving_load_results = example_bridge.get_results()

where,

* basic_load_case_result : a data array for non-moving load cases.
* moving_load_results: a list of data array for each moving load cases defined.

Each data array contains dimensions of"

* load case : listing all load case
* Node : listing all nodes within mesh of grillage model
* Component: Node responses ordered in this manner - dx,dy,dz,theta_x,theta_y,theta_z,Vx,Vy,Vz,Mx,My,Mz

From here, users can use xarray's function for data array to extract 'slices' of data


