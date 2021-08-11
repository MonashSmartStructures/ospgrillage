========================
Performing analysis
========================

Having created the grillage model, users can proceed with grillage analysis.
The *ospgrillage* module contains grillage analysis utilities which wraps ``OpenSeesPy`` commands to perform load analysis.
This allow users to specify load cases comprising of multiple loads types and then run load case analysis.
Furthermore, *ospgrillage* module also options for moving load analysis.


Defining loads
------------------------

Loads are created with the interface function ``create_load()``. Users pass argument for `type=` to specify the load type.
Available loads types include `Point`_, `Line`_, and `Patch`_ loads.


[picture]


Each load type requires user to specify its load point(s). This is achieved by a namedTuple `LoadPoint(x,y,z,p)` where `x`,`y`,`z` are the coordinates of the load point
and `p` is the magnitude of the vertical loading. Note, `p` is a unit magnitude which is interpreted differently based on the load type - this will be later explained.

.. code-block:: python

    point_load_location = ospg.create_load_vertices(x=5, y=0, z=2, p=20)  # create load point


Depending on the load type, a minimum number of LoadPoint namedTuple are required.
These are set to each load type's `point#=` variable for the load type class for the global coordinate system,
or else `local_point_#=` variable for a user-defined local coordinate system, where # is a digit from 1 to 9.


Loads are generally in the global coordinate system with respect to the created grillage model.
However, a user-defined local coordinate system may also be used to assist in then creating `Compound load`_ later on.

.. _Point:

Point Loads
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Point load is a force applied on a single infinitesmal point of the grillage model.
Point loads are used represent a large range of loads, such as truck axle, or superimposed dead load on a deck.


[picture]


Point load takes only a single `LoadPoint` tuple. `p` in the tuple should have units of force (eg. N, kN, kips, etc).

The following example code creates a 20 force unit point load located at (5,0,2) in the global coordinate system.

.. code-block:: python

    point_load_location = ospg.create_load_vertices(x=5, y=0, z=2, p=20)  # create load point
    Single = ospg.create_load(type="point",name="single point", point1=point_load_location)

To position the load instead in a user defined local coordinate system to later create a `Compound Load`_, the variable `localpoint1` instead of `point1` is used.

.. code-block:: python

    point_load_location = ospg.create_load_vertices(5, 0, 2, 20)  # create load point
    Single = ospg.create_load(type="point",name="single point", localpoint1=point_load_location)


.. _Line:

Line Loads
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Line loads are loads exerted along a line. Line loads are useful to represent loads such as self weight of longitudinal beams or
distributed load on beam elements along the span direction.

[picture]

Line loads are instantiated with the interface function ``create_load(type="line)`` and required at least two :class:`LoadPoint` tuple (corresponds to the start and end of the line load).
Using more than two tuples allows a curve line loading profile.
`p` in the :class:`LoadPoint` tuple should have units of force per distance (eg. kN/m, kips/ft, etc).

The following example code is a constant 2 force per distance unit line load (UDL)
in the global coordinate system from -1 to 11 distance units in the `x`-axis and along the position in the `z`-axis at 3 distance units.

.. code-block:: python

    barrier_point_1 = ospg.LoadPoint(-1, 0, 3, 2)
    barrier_point_2 = ospg.LoadPoint(11, 0, 3, 2)
    Barrier = ospg.create_load(type="line", name="Barrier curb", point1=barrier_point_1, point2=barrier_point_2)

As before, to position the load instead in a user defined local coordinate system to later create a `Compound load`_ loads, the variable `localpoint` instead of `point` is used.

.. _Patch:

Patch loads
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Patch loads are useful to represent loads distributed uniformly over a certain area such as traffic lanes.

[picture]

Patch loads are instantiated with the interface function ``create_load(type="patch)``, or directly
using :class:`PatchLoading`. Patch load requires at least four :class:`LoadPoint` tuple (corresponds to the vertices of the patch load).
Using eight tuples allows a curve surface loading profile.
`p` in the :class:`LoadPoint` tuple should have units of force per area.

The following example code creates a constant 5 force per area unit patch load
in the global coordinate system. 
To position the load instead in a user defined local coordinate system, the variable `localpoint` instead of `point` is used.

.. code-block:: python

    lane_point_1 = ospg.LoadPoint(0, 0, 3, 5)
    lane_point_2 = ospg.LoadPoint(8, 0, 3, 5)
    lane_point_3 = ospg.LoadPoint(8, 0, 5, 5)
    lane_point_4 = ospg.LoadPoint(0, 0, 5, 5)
    Lane = ospg.create_load(type="patch",name="Lane 1", point1=lane_point_1, point2=lane_point_2, point3=lane_point_3, point4=lane_point_4)

.. _Compound load:

Compound loads
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Two or more of these load types can be combined to form `Compound load`_ loads. All load types are applied in the direction of the global `y`-axis.
Loads in other directions and applied moments are currently not supported.

[picture]

To create a compound load, use the ``create_compound_load()`` function or the
:class:`CompoundLoad` class - passing load objects for compounding as input parameters.

The following code creates and add a point and line load to the :class:`CompoundLoad` object.

.. code-block:: python

    # components in a compound load
    wheel_1 = ospg.create_load(type="point", point1= ospg.LoadPoint(0, 0, 3, 5))  # point load 1
    wheel_2 = ospg.create_load(type="point", point1= ospg.LoadPoint(0, 0, 3, 5))  # point load 2

After creating a compound load, users will have to add :class:`~Loads` objects (Point, Line, Patch) to the Compound load object:

.. code-block:: python

    C_Load = ospg.create_compound_load(name = "Axle tandem")  # constructor of compound load
    C_Load.add_load(load_obj=wheel_1)
    C_Load.add_load(load_obj=wheel_2)

After defining all required load objects, :class:`~CompoundLoad` requires users to define the global coordinate to map the origin of user-defined local coordinates
to the global coordinate space. This is done using ``set_global_coord()`` function, passing a Point namedTuple
If not specified, the mapping's reference point is default to the **Origin** of coordinate system i.e. (0,0,0)

For example, this code line sets the **Origin** as well as load points for all load objects of **C_load**  by x + 4, y + 0 , and z + 3.

.. code-block:: python

    C_Load.set_global_coord(Point(4,0,3))

Here are the valid input types for which CompoundLoad accepts:

.. list-table:: Table: 1 Valid combinations for CompoundLoad object
   :widths: 25 25 25 25
   :header-rows: 1

   * - Load's coordinate space
     - `local_coord=`
     - Description
     - Require `set_global_coord()`?
   * - Global
     - No
     - Sets the Load's points to global space
     - No
   * - Global
     - Yes
     - Overwrites the Load's global space, keeping only the Magnitude of the global load
     - Yes
   * - Local
     - No
     - Sets the Load's local space, later set to global using `set_global_coord()`
     - Yes
   * - Local
     - Yes
     - **Invalid combination**, loads are defined in local space already
     - N/A


**Coordinate System**

When adding each load object, the :class:`~CompoundLoad` class allow users to input a ``load_coord=`` keyworded parameter.
This relates to the load object - whether it was previously defined in the user-defined *local* or in the *global* coordinate system. The following explains the various
input conditions


.. note::

    Compound loads require users to pay attention between basic and global coordinate system (see :ref:`ModuleDoc` for more information on coordinate systems)

    At the current stage, the :class:`~CompoundLoad` parses the load object within **local coordinate system**. When pass as input into :class:`~LoadCase`, the Compound load's vertices / load points
    are automatically converted to **global coordinates**, based on the inputs of ``set_global_coord`` function


.. _load cases:

Load cases
______________________
Load cases are a set of load types (`Point`_, `Line`_, `Patch`_, `Compound load`_) used to define a particular loading condition. Compound loads are treated as a single load group within a load case
having same reference points (e.g. tandem axle) and properties (e.g. load factor)

After load type objects are created, users add the load objects to :class:`LoadCase` class objects. First, users instantiates a
:class:`LoadCase` class object and giving it its name.

.. code-block:: python

    DL = create_load_case(name="Dead Load")

Users then pass load objects as input parameters using ``add_load_groups()`` function. The following code line shows how
the above load types are added to *DL* load case.

.. code-block:: python

    DL.add_load_groups(Single)  # each line adds individual load types to the load case
    DL.add_load_groups(Barrier)
    DL.add_load_groups(Lane)

After adding loads, the :class:`LoadCase` object is added to grillage model for analysis using the ``add_load_case()``
function of :class:`OspGrillage` class. Users repeat this step for any defined load cases.

.. code-block:: python

    example_bridge.add_load_case(DL)  # adding this load case to grillage model


Moving loads
------------------------
For moving load analysis, users create moving load objects using :class:`MovingLoad` class. The moving load class takes a load type object (`Point`_, `Line`_, `Patch`_, `Compound load`_) and moves the load
through a path points described by a :class:`Path` object and obtained by the ``get_path_points()`` method. 
Path are defined using two namedTuple :class:`Point(x,y,z)` to describe its start and end position.

The following example code is two point loads defined as a moving load travelling a path from 2 to 4 distance units in the global coordinate system.

.. code-block:: python

    front_wheel = ospg.create_load_vertices(x=0, y=0, z=0, p=6)   # load point 1
    back_wheel = ospg.create_load_vertices(x=-1, y=0, z=0, p=6)   # load point 2
    Line = ospg.create_load(type="line",local_point_1=front_wheel,local_point_2=back_wheel)
    tandem = ospg.create_compound_load("Two wheel vehicle")

    single_path = ospg.create_moving_path(start_point=ospg.Point(2,0,2), end_point= ospg.Point(4,0,2))  # create path object
    move_line = ospg.create_moving_load(name="Line Load moving") # moving load obj
    move_line.set_path(single_path)   # set path
    move_line.add_loads(load_obj=Line)  # add compound load to moving load


From here, use the ``add_load_case()`` function of the :class:`OspGrillage` to add the moving load. Here, the function automatically
creates multiple `load cases`_ which corresponds to the load condition as the load moves through each increment of the path.

.. code-block:: python

    example_bridge.add_load_case(move_point)

Defining load combination
------------------------
Load combinations are defined by passing an input dictionary of basic load case name as keys with load factors as
values. An example dictionary is shown as follows, here we create a combination where `Dead Load` and `Live Load` Load
Cases are multiplied by 1.2 and 1.7 respectively.

.. code-block:: python

    load_combinations = {'Dead Load':1.2,'Live traffic':1.7}

After defining the load combination input, users add the input to analysis using the function ``add_load_combination()``.

.. code-block:: python

    example_bridge.add_load_combination(name = "ULS", input_dict = load_combinations )

Load combinations are automatically calculated from analysis results at the end after all load cases were analyzed.
The following **Obtaining results** section will explain how these load combinations are extracted.

Running analysis
------------------------

Once all defined load cases (static and moving) have been added to the grillage the analysis can be conducted.

To analyse loadcase(s), users run the class function ``analyze()``. This function takes either keyword arguments
``all=`` or ``loadcase=``. When ``all=True``, ``analyze()`` will run all defined load cases. If users wish to run only
a specific set of load cases, pass a list of load case name str to ``loadcase=``  keyword. This will analyse all load cases of the list.
Here are a few interface examples of ``analyze()``.

.. code-block:: python
    # run either one
    example_bridge.analyze(all = True)
    # or a single str
    example_bridge.analyze(load_case="DL")
    # or a single element list
    example_bridge.analyze(load_case=["DL"])
    # or a list of multiple load cases
    example_bridge.analyze(load_case=["DL","SDL"])


Obtaining results
__________________________________
Results are returned by running ``get_results()`` function.
The results are returned as `an xarray's DataSet <http://xarray.pydata.org/en/stable/user-guide/data-structures.html#>`_ (python's ```Xarray``` module).


.. code-block:: python

    results =  example_bridge.get_results(all=True)

The *results* dataset contains array variables with dimensions in brackets:

* displacement (Loadcase, Node, Component)
* forces (Loadcase, Element, Component)

For elements, an additional array variable contains information on element nodes.

* ele_nodes (Element, Nodes)

where Nodes is a 2-D array

The *results* dataset contains dimensions of:

* Component: Node responses ordered in this manner - dx,dy,dz,theta_x,theta_y,theta_z,Vx,Vy,Vz,Mx,My,Mz
* Loadcase: name string of load case - list of str
* Node: Node numbers of model- list of int


Here is an example of how the data array looks like in practice:

..  figure:: ../images/stucture_dataarray.PNG
    :align: center
    :scale: 75 %

Additionally,

From here, users can use xarray's function for data array to extract 'slices' of data.

Obtaining load combinations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For load combinations, users passes `get_combination=` argument as *True* to ``get_results()``.

.. code-block:: python

    load_combination_dict = example_bridge.get_results(get_combinations=True)

Instead of a single data set, the function returns a single dict with names of load combinations as key, paired with a data array
of the load combination as its value. The data array has the same dimensions as those from standard
load case data set, only this time the arrays are modified by load factors defined for the load combinations.

Here is how the structure of a `load_combination_dict` looks like:

[picture]

Obtaining specific load case results
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
By default, ```get_results()``` returns results of all defined load cases (be it basic or moving).
If users wish to extract results of a specific load case (e.g. moving load), users pass in a single or a `list`
of name string(s) of the specific load cases to keyword argument `load_case =`

.. code-block:: python

    moving_load_results = example_bridge.get_results(load_case="M1600")

The above code will return a data set containing only the incremental load cases for each position of the "M1600" moving load.

