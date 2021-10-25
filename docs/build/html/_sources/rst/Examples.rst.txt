========================
Examples
========================
Here are some examples of what you can do with *ospgrillage* module.

Super T bridge model
------------------------------------------------------------
This example reproduces the grillage model of a super-T bridge from Caprani et al. (2017). In that study,
the LUSAS commercial software is used to create the grillage model. Figure 1 shows the Super-T deck cross-section.

..  figure:: ../../_images/example_cross_section.PNG
    :align: center
    :scale: 25 %

    Figure 1: Super-T deck cross section (after Caprani et al., 2017).


Creating the grillage
^^^^^^^^^^^^^^^^^^^^^^^^

For this example, the five super-T beams and two edge beams (parapets) of Figure 1 are being modelled similar to Caprani et al. (2017)
- with the number of longitudinal and transverse grid lines being 7 and 11 respectively.

.. code-block:: python

    import numpy as np
    import ospgrillage as og

    # Adopted units: N and m
    kilo = 1e3
    milli = 1e-3
    N = 1
    m = 1
    mm = milli*m
    m2 = m**2
    m3 = m**3
    m4 = m**4
    kN = kilo*N
    MPa = N/((mm)**2)
    GPa = kilo*MPa

    # define material
    concrete = og.create_material(type="concrete", code="AS5100-2017", grade="65MPa")

    # define sections (parameters from LUSAS model)
    edge_longitudinal_section= og.create_section(A=0.934*m2,J=0.1857*m3, Iz=0.3478*m4, Iy=0.213602*m4,
                                               Az=0.444795*m2, Ay=0.258704*m2)

    longitudinal_section = og.create_section(A=1.025*m2, J=0.1878*m3, Iz=0.3694*m4,Iy=0.113887e-3*m4,
                                                    Az=0.0371929*m2, Ay=0.0371902*m2)


    transverse_section = og.create_section(A=0.504*m2, J=5.22303e-3*m3, Iy=0.32928*m4, Iz=1.3608e-3*m4,
                                             Ay=0.42*m2, Az=0.42*m2)

    end_transverse_section = og.create_section(A=0.504/2*m2, J=2.5012e-3*m3, Iy=0.04116*m4, Iz=0.6804e-3*m4,
                                                 Ay=0.21*m2, Az=0.21*m2)

     # define grillage members
    longitudinal_beam = og.create_member(section=longitudinal_section, material=concrete)
    edge_longitudinal_beam = og.create_member(section=edge_longitudinal_section, material=concrete)
    transverse_slab = og.create_member(section=transverse_section, material=concrete)
    end_transverse_slab = og.create_member(section=end_transverse_section, material=concrete)

    # parameters of bridge grillage
    L = 33.5*m # span
    w = 11.565*m # width
    n_l = 7 # number of longitudinal members
    n_t = 11 # number of transverse members
    edge_dist = 1.05*m # distance between edge beam and first exterior beam
    angle = 0 # skew angle

    # create grillage
    simple_grid = og.create_grillage(bridge_name="Super-T 33_5m", long_dim=L, width=w, skew=angle,
                                   num_long_grid=n_l, num_trans_grid=n_t, edge_beam_dist=edge_dist)

    # assign grillage member to element groups of grillage model
    simple_grid.set_member(longitudinal_beam, member="interior_main_beam")
    simple_grid.set_member(longitudinal_beam, member="exterior_main_beam_1")
    simple_grid.set_member(longitudinal_beam, member="exterior_main_beam_2")
    simple_grid.set_member(edge_longitudinal_beam, member="edge_beam")
    simple_grid.set_member(transverse_slab, member="transverse_slab")
    simple_grid.set_member(end_transverse_slab, member="start_edge")
    simple_grid.set_member(end_transverse_slab, member="end_edge")

    # create the model in OpenSees
    simple_grid.create_osp_model(pyfile=False) # pyfile will not (False) be generated for further analysis (should be create_osp?)
    og.opsplt.plot_model("nodes") # plotting using Get_rendering
    og.opsv.plot_model(az_el=(-90, 0)) # plotting using ops_vis

Figure 2 shows the plotted model in OpenSees model space.

..  figure:: ../../_images/33m_bridge.PNG
    :align: center
    :scale: 75 %

    Figure 2: Grillage model of the exemplar 33.5 m bridge.

Adding load cases to model
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Here we create and add load cases to the `simple_grid` model for analysis.

First load case is a line load running along mid span width.

.. code-block:: python

    # reference unit load for various load types
    P = 1*kN
    # name strings of load cases to be created
    static_cases_names = ["Line Test Case","Points Test Case (Global)","Points Test Case (Local in Point)",
                         "Points Test Case (Local in Compound)","Patch Test Case"]

    # Line load running along midspan width (P is kN/m)
    # Create vertical load points in global coordinate system
    line_point_1 = og.create_load_vertex(x=L/2, z=0, p=P)
    line_point_2 = og.create_load_vertex(x=L/2, z=w, p=P)
    test_line_load = og.create_load(type='line',name="Test Load", point1=line_point_1, point2=line_point_2)

    # Create load case, add loads, and assign
    line_case = og.create_load_case(name=static_cases_names[0])
    line_case.add_load(test_line_load)

    simple_grid.add_load_case(line_case)

Second load case comprise of Compounded point loads

.. code-block:: python

    # Compound point loads along midspan width (P is kN)
    # working in global coordinate system
    p_list = [0,edge_dist,edge_dist+2*m,edge_dist+4*m,edge_dist+6*m,w-edge_dist,w] # creating list of load position

    test_points_load = og.create_compound_load(name="Points Test Case (Global)")

    # create point load in global coordinate
    for p in p_list:
        point = og.create_load(type='point',name="Point",point1=og.create_load_vertex(x=L/2, z=p, p=P))
        # add to compound load
        test_points_load.add_load(load_obj = point)

    # Create load case, add loads, and assign
    points_case = og.create_load_case(name=static_cases_names[1])
    points_case.add_load(test_points_load)

    simple_grid.add_load_case(points_case)

Third load case is identical to the second load case with Compounded point loads, but this time defining Compound loads
in Local coordinates then setting the local coordinate system of compound load to global of grillage.

.. code-block:: python

    # Compound point loads along midspan width
    # working in user-defined local coordinate (in point load)
    test_points_load = og.create_compound_load(name="Points Test Case (Local in Point)")

    # create point load in local coordinate space
    for p in p_list:
        point = og.create_load(type='point',name="Point",point1=og.create_load_vertex(x=0, z=p, p=P))
        # add to compound load
        test_points_load.add_load(load_obj = point)

    # shift from local to global
    test_points_load.set_global_coord(og.Point(L/2,0,0))

    # Create load case, add loads, and assign
    points_case = og.create_load_case(name=static_cases_names[2])
    points_case.add_load(test_points_load)

    simple_grid.add_load_case(points_case)

Fourth load case entails a patch load

.. code-block:: python

    # Patch load over entire bridge deck (P is kN/m2)
    patch_point_1 = og.create_load_vertex(x=0, z=0, p=P)
    patch_point_2 = og.create_load_vertex(x=L, z=0, p=P)
    patch_point_3 = og.create_load_vertex(x=L, z=w, p=P)
    patch_point_4 = og.create_load_vertex(x=0, z=w, p=P)
    test_patch_load = og.create_load(type='patch',name="Test Load",
                                       point1=patch_point_1, point2=patch_point_2,
                                       point3=patch_point_3, point4=patch_point_4)

    # Create load case, add loads, and assign
    patch_case = og.create_load_case(name=static_cases_names[4])
    patch_case.add_load(test_patch_load)
    simple_grid.add_load_case(patch_case)


Adding a moving load analysis
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Here's how we create and add a moving load (e.g. a truck) to the 28 m bridge model.

.. code-block:: python

    # 2 axle truck (equal loads, 2x2 spacing centre line running)
    axl_w = 2*m # axle width
    axl_s = 2*m # axle spacing
    veh_l = axl_s # vehicle length
    # create truck in local coordinate system
    two_axle_truck = og.create_compound_load(name="Two Axle Truck")
    # note here we show that we can directly interact and create load vertex using LoadPoint namedtuple instead of create_load_vertex()
    point1 = og.create_load(type="point",name="Point",point1=og.LoadPoint(x=0, y=0, z=0, p=P))
    point2 = og.create_load(type="point",name="Point",point1=og.LoadPoint(x=0, y=0, z=axl_w, p=P))
    point3 = og.create_load(type="point",name="Point",point1=og.LoadPoint(x=axl_s, y=0, z=axl_w, p=P))
    point4 = og.create_load(type="point",name="Point",point1=og.LoadPoint(x=axl_s, y=0, z=0, p=P))

    two_axle_truck.add_load(load_obj = point1)
    two_axle_truck.add_load(load_obj = point2)
    two_axle_truck.add_load(load_obj = point3)
    two_axle_truck.add_load(load_obj = point4)

    # create path object in global coordinate system - centre line running of entire span
    # when local coord: the path describes where the moving load *origin* is to start and end
    single_path = og.create_moving_path(start_point=og.Point(0-axl_w,0,w/2-axl_w/2),
                                          end_point=og.Point(L,0,w/2-axl_w/2),
                                          increments=int(L+veh_l+1))


    # create moving load (and case)
    moving_truck = og.create_moving_load(name="Moving Two Axle Truck")

    # Set path to all loads defined within moving_truck
    moving_truck.set_path(single_path)
    # note: it is possible to set different paths for different compound loads in one moving load object
    moving_truck.add_loads(two_axle_truck)

    # Assign
    simple_grid.add_load_case(moving_truck)


Analysis
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Analyzing all defined load case

.. code-block:: python

    # Run analysis
    simple_grid.analyze()


Getting load case results
^^^^^^^^^^^^^^^^^^^

Get `xarray` DataSet of results.

.. code-block:: python

    results = simple_grid.get_results() # gets basic results

For information on :func:`~ospgrillage.osp_grillage.OspGrillage.get_results` variable, see :ref:`PostProcessing`.

Getting load combination results
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    l_factor = 2.3
    p_factor = 0.5
    # combination with line load case and patch load case
    load_combinations = {static_cases_names[0]:l_factor,static_cases_names[-1]:p_factor}
    combination_results = simple_grid.get_results(combinations=load_combinations)

Refer to :ref:`Running_analysis` for more information on the `xarray` formats for load combinations.

Data processing
^^^^^^^^^^^^^^^^^^^
Having the results be in `xarray` DataSet, we can do many things with it such as slicing and query its data.

The following example shows how to extract bending moments in midspan - the critical location for the defined load cases.

First for static load cases, we extract moments in global z for each `i` node of grillage member (since `i` node correspond to the nodes in the mid span).

.. code-block:: python

    # get list of longitudinal element tags along/near mid_span i.e. 84 to 90 in Figure 1
    ele_set = list(range(84, 90 + 1))
    # query
    extracted_bending = results.forces.sel(Loadcase=static_cases_names, Element=ele_set, Component="Mz_i")


`extracted_bending` variable holds the load case for 'Line Test Case', 'Point Test Case(Global)', 'Points Test Case (Local in Point)',
'Points Test Case (Local in Compound)', 'Patch Test Case'.

Should we sum the nodal forces from members on one side, we expect approximate equal PL/4 (similar) or sum of the following
lusas plot

.. code-block:: python

    np.sum(np.array(results.forces.sel(Loadcase=static_cases_names, Element=ele_set, Component="Mz_i")),axis=1)



Process load combinations results
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Here we sum the nodal forces from the mid span - `i` node
.. code-block:: python

    sum_node_force = np.sum(np.array(combo_results.forces.sel(Element=ele_set, Component="Mz_i")))


Extract and process moving load results
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Here we :ref:`access results` of the moving load case.

.. code-block:: python

    # call the results and
    move_results = simple_grid.get_results(load_case="Moving Two Axle Truck")

One can query results at specific position of the moving load by looking up the index of load case. The following example
we query the bending moment about z-axis component, with
load case corresponding to where the load groups are at/near midspan L = 16.75 m, and the longitudinal elements along/near
mid-span, i.e. element 84 to 90 in Figure 1:

.. code-block:: python

    # selecting load case of specific load position
    integer = int(L/2 - 1 + 2)  # here we choose when the load groups are at/near mid span L = 14m i.e. 17

    # query
    mid_span_bending = move_results.forces.isel(Loadcase=integer).sel(Element=ele_set,Component="Mz_i")


Finally, summing the query of bending moment and comparing with theoretical calculation:

.. code-block:: python

    bending_z = np.sum(np.array(mid_span_bending))

    # Hand calc:
    bending_z_theoretical = 2*P*(L/2-axl_s/2) # 31500

    print("bending_z ={}".format(bending_z))
    print("bending_z_theoretical ={}".format(bending_z_theoretical))

The following is printed to terminal (units in N m) :

.. code-block:: python

    bending_z = 31499.999999999913
    bending_z_theoretical = 31500.0


Super-T bridge model using shell hybrid model type
------------------------------------------------------------
Here we recreate the previous 33.5 m super-T bridge using the shell hybrid model type.

.. code-block:: python

    import numpy as np
    import ospgrillage as og

    # Adopted units: N and m
    kilo = 1e3
    milli = 1e-3
    N = 1
    m = 1
    mm = milli*m
    m2 = m**2
    m3 = m**3
    m4 = m**4
    kN = kilo*N
    MPa = N/((mm)**2)
    GPa = kilo*MPa

    # define material
    concrete = og.create_material(type="concrete", code="AS5100-2017", grade="65MPa")

    # define sections (parameters from LUSAS model)
    edge_longitudinal_section= og.create_section(A=0.934*m2,J=0.1857*m3, Iz=0.3478*m4, Iy=0.213602*m4,
                                               Az=0.444795*m2, Ay=0.258704*m2)

    longitudinal_section = og.create_section(A=1.025*m2, J=0.1878*m3, Iz=0.3694*m4,Iy=0.113887e-3*m4,
                                                    Az=0.0371929*m2, Ay=0.0371902*m2)


    transverse_section = og.create_section(A=0.504*m2, J=5.22303e-3*m3, Iy=0.32928*m4, Iz=1.3608e-3*m4,
                                             Ay=0.42*m2, Az=0.42*m2)

    end_transverse_section = og.create_section(A=0.504/2*m2, J=2.5012e-3*m3, Iy=0.04116*m4, Iz=0.6804e-3*m4,
                                                 Ay=0.21*m2, Az=0.21*m2)

     # define grillage members
    longitudinal_beam = og.create_member(section=longitudinal_section, material=concrete)
    edge_longitudinal_beam = og.create_member(section=edge_longitudinal_section, material=concrete)
    transverse_slab = og.create_member(section=transverse_section, material=concrete)
    end_transverse_slab = og.create_member(section=end_transverse_section, material=concrete)

    # parameters of bridge grillage
    L = 33.5*m # span
    w = 11.565*m # width
    n_l = 7 # number of longitudinal members
    n_t = 11 # number of transverse members
    edge_dist = 1.05*m # distance between edge beam and first exterior beam
    angle = 0 # skew angle
    offset_beam_y = 0.499*m
    max_mesh_size_z = 1*m
    max_mesh_size_x = 1*m
    link_nodes_width = 0.89*m

    # create grillage - shell model variant
    simple_grid = og.create_grillage(bridge_name="Super-T 33_5m", long_dim=L, width=w, skew=angle,
                                   num_long_grid=n_l, num_trans_grid=n_t, edge_beam_dist=edge_dist,
                                   model_type="shell_beam", max_mesh_size_z=max_mesh_size_z,max_mesh_size_x=max_mesh_size_x,
                                   offset_beam_y_dist=offset_beam_y,link_nodes_width=link_nodes_width)

    # assign grillage member to element groups of grillage model
    simple_grid.set_member(longitudinal_beam, member="interior_main_beam")
    simple_grid.set_member(longitudinal_beam, member="exterior_main_beam_1")
    simple_grid.set_member(longitudinal_beam, member="exterior_main_beam_2")
    simple_grid.set_member(edge_longitudinal_beam, member="edge_beam")
    simple_grid.set_member(transverse_slab, member="transverse_slab")
    simple_grid.set_member(end_transverse_slab, member="start_edge")
    simple_grid.set_member(end_transverse_slab, member="end_edge")

    # create the model in OpenSees
    simple_grid.create_osp_model(pyfile=False) # pyfile will not (False) be generated for further analysis (should be create_osp?)
    og.opsplt.plot_model("nodes") # plotting using Get_rendering
    # ops_vis does not work for hybrid model

..  figure:: ../../_images/33m_bridge_shell.PNG
    :align: center
    :scale: 25 %

    Figure 3: 33.5m exemplar bridge built with shell hybrid model.


Oblique vs Orthogonal Mesh
---------------------------
Here are some more examples showing the two types of meshes by altering the ``mesh_typ`` input of
:func:`~ospgrillage.osp_grillage.create_grillage`.


* 28 m bridge with :func:`Oblique` mesh - positive 20 degree

.. code-block:: python

    example_bridge = og.create_grillage(bridge_name="Oblique_28m", long_dim=10, width=7, skew=20,
                             num_long_grid=7, num_trans_grid=5, edge_beam_dist=1, mesh_type="Oblique")


..  figure:: ../../_images/standard_oblique.PNG
    :align: center
    :scale: 25 %

    Figure 4: Grillage with oblique mesh


* 28 m bridge with :func:`Ortho` mesh

.. code-block:: python

    example_bridge = og.create_grillage(bridge_name="Ortho_28m", long_dim=10, width=7, skew=20,
                             num_long_grid=7, num_trans_grid=5, edge_beam_dist=1, mesh_type="Ortho")


..  figure:: ../../_images/standard_ortho.PNG
    :align: center
    :scale: 25 %

    Figure 5: Grillage with orthogonal


Skew edges of mesh
--------------------
Here is an example showing the types of edge skew you can produce with *ospgrillage*.
A version the aforementioned 28m grillage model example is given but
with different parameters for its grillage object i.e. :func:`~ospgrillage.osp_grillage.OspGrillage.create_grillage`.
This time we have varied span to 10 m, and edge skew angles - left edge is 42 degrees, right edge is 0 degrees (orthogonal).

The following portion of the code is altered which then produces a grillage model with mesh as shown in Figure 6:

.. code-block:: python

    example_bridge = og.create_grillage(bridge_name="SuperT_10m", long_dim=10, width=7, skew=[42, 0],
                             num_long_grid=7, num_trans_grid=5, edge_beam_dist=1, mesh_type="Ortho")

    example_bridge.create_ops(pyfile=False)
    og.opsplt.plot_model("nodes")


..  figure:: ../../_images/42_0_mesh.PNG
    :align: center
    :scale: 25 %

    Figure 6: Orthogonal mesh with left and right edge angle of 42 and 0 respectively.