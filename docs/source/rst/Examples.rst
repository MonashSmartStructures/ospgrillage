========================
Examples
========================
Here are some more examples of what you can do with *ops-grillage* module.


28 m super T bridge model with orthogonal mesh
--------------------

.. code-block:: python

    import ospgrillage as og

    # Units
    meter = 1.0
    N = 1.0
    sec = 1.0
    m2 = meter**2
    m4 = meter**4
    MPa = 1e9*N/m2
    g = 9.81*m/sec**2  # 9.81 m/s2

    # variables
    E = 34.7*MPa
    G = 20e9*MPa # Pa
    v = 0.3
    # bridge geometric properties
    L = 28*m
    H = 7*m
    edge_skew = 0   # both edge orthogonal
    edge_dist = 1.0875  # distance between edge beam and exterior beams
    trans_grid_lines = 14
    long_grid_lines = 7

    # Create materials
    concrete = og.create_material(type="concrete", code="AS5100-2017", grade="50MPa")
    # Define sections
    super_t_beam_section = og.create_section(A=1.0447*m2,J=0.230698*m4, Iy=0.231329*m4, Iz=0.533953*m4,Ay=0.397032*m2, Az=0.434351*m2)


    transverse_slab_section = og.create_section(A=0.5372*m2,J=2.79e-3*m4, Iy=0.3988 / 2 *m4, Iz=1.45e-3 / 2*m4,Ay=0.447 / 2*m2, Az=0.447 / 2*m2, unit_width=True)


    end_tranverse_slab_section = og.create_section(A=0.5372 / 2*m2,J=2.68e-3*m4, Iy=0.04985*m4,Iz=0.725e-3*m4,Ay=0.223*m2, Az=0.223*m2)

    edge_beam_section = og.create_section(A=0.039375*m2,J=0.21e-3*m4, Iy=0.1e-3*m4,Iz=0.166e-3*m4,Ay=0.0328*m2, Az=0.0328*m2)

    # define grillage members
    super_t_beam = og.create_member(member_name="Intermediate I-beams", section=super_t_beam_section, material=concrete)
    transverse_slab = og.create_member(member_name="concrete slab", section=transverse_slab_section, material=concrete)
    edge_beam = og.create_member(member_name="exterior I beams", section=edge_beam_section, material=concrete)
    end_transverse_slab = og.create_member(member_name="edge transverse", section=end_transverse_slab_section,
                                           material=concrete)

    bridge_28 = og.create_grillage(bridge_name="SuperT_28m", long_dim=L, width=H, skew=edge_skew,
                            num_long_grid=long_grid_lines, num_trans_grid=trans_grid_lines, edge_beam_dist=edge_dist, mesh_type="Ortho")

    # set grillage member to element groups of grillage model
    bridge_28.set_member(super_t_beam, member="interior_main_beam")
    bridge_28.set_member(super_t_beam, member="exterior_main_beam_1")
    bridge_28.set_member(super_t_beam, member="exterior_main_beam_2")
    bridge_28.set_member(edge_beam, member="edge_beam")
    bridge_28.set_member(transverse_slab, member="transverse_slab")
    bridge_28.set_member(end_tranverse_slab, member="start_edge")
    bridge_28.set_member(end_tranverse_slab, member="end_edge")

    bridge_28.create_ops(pyfile=False)
    # plot model
    og.opsplt.plot_model("nodes")

Figure 1 shows the plotted model in Opensees model space.

..  figure:: ../../_images/28m_bridge.png
    :align: center
    :scale: 75 %

    Figure 1: Grillage model of the exemplar 28 m bridge.

Adding DL and SDL to analysis
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Adding basic load cases, i.e.

.. code-block:: python

    dead_load = create_load("DL",point1=point1,point2=point2)
    dead_load = create_load("DL",point1=point1,point2=point2)

Adding a load combination for SDL and DL
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
To define load combinations, users provide a python dictionary with key being the name string of the defined load cases
and value being the load factor to be applied for load combination.

.. code-block:: python
    uls_dict = {"DL":1.2,"SDL":1.5}
    sls_dict = {}
    bridge_28.add_load_combination(load_combination_name="ULS", load_case_and_factor_dict=uls_dict) # add ULS combination
    bridge_28.add_load_combination(load_combination_name="SLS", load_case_and_factor_dict=sls_dict) # add SLS combination


Adding a moving load analysis
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Here we add a moving load analysis to the 28 m bridge model

.. code-block:: python

    front_wheel = og.create_point_load(name="front wheel", point1=LoadPoint(2, 0, 2, 50))  # Single point load 50 N

    single_path = og.create_moving_path(start_point=Point(0, 0, 2), end_point=Point(29, 0, 3))  # create path object
    move_point = og.create_moving_load(name="single_moving_point")
    move_point.set_path(single_path)
    move_point.add_loads(load_obj=front_wheel)
    bridge_28.add_load_case(move_point)

    bridge_28.analyze()
    results = bridge_28.get_results()


Processing results
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The following lines of code shows how we can process the output data array - demonstrated for the Moving load results.

.. code-block:: python

    # Here we can slice data to get a reduced data array for the outputs
    # query mid point shear force during truck movement
    results.sel(Node=63,Component='dy')
    # query max of slice
    results.sel(Node=63,Component='dy').idxmax()
    # query max and min envelopes of displacement for all nodes - this is done by max/min function across the 'Loadcase' dimension.
    max_dY = results.sel(Component='dy').max(dim='Loadcase')
    min_dY = results.sel(Component='dy').max(dim='Loadcase')

    # See which nodes are i and j for each element
    print(results['ele_nodes'].sel(Element=ele_set,Nodes="i"))

    np.array(results['forces'].sel(Element=ele_set,Component="Mz_i"))

    # sum the nodal forces from the members on one side
    print(np.sum(np.array(results['forces'].sel(Element=ele_set,Component="Mz_i"))))
    # sum should be approximate equal to PL/4 or sum of lusas plot
    # PL/4 = 49000.00

Testing various mesh types for bridge dimensions
--------------------
Here is a version of the aforementioned grillage model with different dimensions and varied edge skew angles - left edge is 42 degrees, right edge is 0 degrees (orthogonal).
Material and section properties follows those of aforementioned model.

.. code-block:: python

    example_bridge = og.create_grillage(bridge_name="SuperT_10m", long_dim=10, width=7, skew=[42, 0],
                             num_long_grid=7, num_trans_grid=5, edge_beam_dist=1, mesh_type="Ortho")

    example_bridge.create_ops(pyfile=False)
    og.opsplt.plot_model("nodes")


..  figure:: ../../images/42_0_mesh.png
    :align: center
    :scale: 75 %

    Figure 2: Grillage model of the exemplar 28 m bridge.