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


.. _Compound load:

Compound loads
__________________________
Two or more groups of load objects can be compounded into a compound load. Compound loads are treated as a single load group within a load case
having same reference points (e.g. tandem axle) and properties (e.g. load factor)

To create a compound load, use the :class:`CompoundLoad` class - passing load objects for compounding as input parameters.

The following code creates and add a point and line load to the :class:`CompoundLoad` object.

.. code-block:: python

    # compound load
    M1600 = CompoundLoad("Lane and Barrier") # lane and barrier compounded

After creating a compound load, users will have to add :class:`~Loads` objects (Point, Line, Patch) to the Compound load object:

.. code-block:: python

    M1600.add_load(load_obj=Single, local_coord=Point(5,0,5))
    M1600.add_load(load_obj=Barrier, local_coord=Point(3,0,5))

When adding each load object, the :class:`~CompoundLoad` class allow users to input a ``load_coord=`` keyworded parameter.
This relates to the load object - whether it was previously defined in *local* or *global* coordinate system. The following explains the various
input conditions

* if Load object was defined in *local* coordinate and ``load_coord=`` is not provided. The local coordinate tied with the Load object precedes.
* if Load object was defined in *local* coordinate and ``load_coord=`` is provided. The local coordinate of ``load_coord=`` parameter precedes.
* if Load object was defined in *global* coordinate and ``load_coord=`` is not provided. Compound load treats the inherited global coordinates as new *local* coordinate
* if Load object was defined in *global* coordinate and ``load_coord=`` is provided. The local coordinate of ``load_coord=`` parameter precedes, the magnitude of load points/vertices carries over to local coordinate.

After defining all required load objects, :class:`~CompoundLoad` requires users to define the global coordinate which to map the basic coordinates. The mapping's reference point is default to the **Origin** of coordinate system
i.e. (0,0,0)

.. code-block:: python

    M1600.set_global_coord(Point(4,0,3))

This last line shifts all load points of all load objects for **Single** and **Barrier** by x + 4, y + 0 , and z + 3.

From this point, the compound loads can be added into `load cases`_ as per ``add_load_groups()`` function.

.. note::

    Compound loads require users to pay attention between basic and global coordinate system (see :ref:`ModuleDoc` for more information on coordinate systems)

    At the current stage, the :class:`~CompoundLoad` parses the load object within **local coordinate system**. When pass as input into :class:`~LoadCase`, the Compound load's vertices / load points
    are automatically converted to **global coordinates**, based on the inputs of ``set_global_coord`` function

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


Defining moving Compound loads
------------------------
Compound loads can be used to describe truck load models where a number of point loads can be compounded to form the
axle forces of a truck. It is then useful to perform moving load analysis by moving the truck (compounded points) model.

The :class:`MovingLoad` class allows such definition when users pass `Compound load`_ object as input for its load
object parameter.



Defining load combination
------------------------
.. note::

    At the current stage, Load combinations are partially supported - there is no function to automatically plot and calculate
    load combinations. To this, users will have to obtain the arrays from the data array output - explained in the next section -
    and apply combination factors manually to the array (generally by array multiplication)

Load combinations analysis are performed by using the :class:`OpsGrillage` function ``add_load_combination()`` function.
Load combinations are defined by passing an input dictionary of basic load case name as keys with load factors as
values. An example dictionary is shown as follows:

.. code-block:: python

    load_combinations = {'ULS-DL':1.2,'Live traffic':1.7}
    example_bridge.add_load_combination(name = "ULS", input_dict = load_combinations )




Obtaining results
------------------------
Results are returned as `data arrays <http://xarray.pydata.org/en/stable/user-guide/data-structures.html#>`_ (python's Xarray module).
To this, run the ``get_results()`` function and two outputs will be returned:

.. code-block:: python

    basic_load_case_result,moving_load_results = example_bridge.get_results()

where,

* basic_load_case_result : a data array containing results for all non-moving load cases.
* moving_load_results: a list of data array each for a moving load.

Each data array contains dimensions of:

* load case : listing all load case
* Node : listing all nodes within mesh of grillage model
* Component: Node responses ordered in this manner - dx,dy,dz,theta_x,theta_y,theta_z,Vx,Vy,Vz,Mx,My,Mz

Here is an example of how the data array looks like in practice:

..  figure:: ../images/stucture_dataarray.PNG
    :align: center
    :scale: 75 %

From here, users can use xarray's function for data array to extract 'slices' of data

