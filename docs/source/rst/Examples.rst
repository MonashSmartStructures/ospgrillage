========================
Examples
========================
Here are some more examples of what you can do with *ops-grillage* module.


28 m super T bridge model with orthogonal mesh
--------------------

.. code-block:: python

    import opsgrillage as og

    # metric units
    meter = 1.0
    N = 1.0
    sec = 1.0
    MPa = 1e9*N/m**2
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

    # reference super T bridge 28m for validation purpose
    # Members

    concrete = og.create_material(type="concrete", code="AS5100-2017", grade="50MPa")
    # define sections
    super_t_beam_section = og.create_section(A=1.0447,
                                      J=0.230698, Iy=0.231329, Iz=0.533953,
                                      Ay=0.397032, Az=0.434351)
    transverse_slab_section = og.create_section(A=0.5372,
                                         J=2.79e-3, Iy=0.3988 / 2, Iz=1.45e-3 / 2,
                                         Ay=0.447 / 2, Az=0.447 / 2, unit_width=True)
    end_tranverse_slab_section = og.create_section(A=0.5372 / 2,
                                            J=2.68e-3, Iy=0.04985,
                                            Iz=0.725e-3,
                                            Ay=0.223, Az=0.223)
    edge_beam_section = og.create_section(A=0.039375,
                                   J=0.21e-3, Iy=0.1e-3,
                                   Iz=0.166e-3,
                                   Ay=0.0328, Az=0.0328)

    # define grillage members
    super_t_beam = og.create_member(member_name="Intermediate I-beams", section=super_t_beam_section, material=concrete)
    transverse_slab = og.create_member(member_name="concrete slab", section=transverse_slab_section, material=concrete)
    edge_beam = og.create_member(member_name="exterior I beams", section=edge_beam_section, material=concrete)
    end_tranverse_slab = og.create_member(member_name="edge transverse", section=end_tranverse_slab_section,
                                           material=concrete)

    bridge_28 = og.OpsGrillage(bridge_name="SuperT_28m", long_dim=L, width=H, skew=edge_skew,
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
    og.opsplt.plot_model("nodes")

The following model is created in Opensees model space.

..  figure:: ../../images/28m_bridge.png
    :align: center
    :scale: 75 %

    Figure 1: Grillage model of the exemplar 28 m bridge.

Adding DL and SDL to analysis
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: python

    test

Adding a load combination for SDL and DL
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
To define load combinations, users provide a python dictionary with key being the name string of the defined load cases
and value being the load factor to be applied for load combination.

.. code-block:: python
    uls_dict = {}
    sls_dict = {}
    bridge_28.add_load_combination(load_combination_name="ULS", load_case_and_factor_dict=uls_dict) # add ULS combination
    bridge_28.add_load_combination(load_combination_name="SLS", load_case_and_factor_dict=sls_dict) # add SLS combination



Adding a moving load analysis
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Here we add a moving load analysis to the 28 m bridge model

.. code-block:: python

    front_wheel = og.PointLoad(name="front wheel", point1=LoadPoint(2, 0, 2, 50))  # Single point load 50 N

    single_path = og.Path(start_point=Point(0, 0, 2), end_point=Point(29, 0, 3))  # create path object
    move_point = og.MovingLoad(name="single_moving_point")
    move_point.add_loads(load_obj=front_wheel, path_obj=single_path.get_path_points())
    move_point.parse_moving_load_cases()
    bridge_28.add_moving_load_case(move_point)

    bridge_28.analyse_moving_load_case()
    results = bridge_28.get_results()


Result acquisition
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

Testing various mesh types for bridge dimensions
--------------------
Here is a grillage model with different edge skew angles - left edge is -42 degrees, right edge is 0 degrees (orthogonal).

.. code-block:: python

    import OpsGrillage as og
    concrete = og.UniAxialElasticMaterial(mat_type="Concrete01", fpc=-6, epsc0=-0.004, fpcu=-6, epsU=-0.014)

    # define sections
    I_beam_section = og.Section(A=0.896, E=3.47E+10,G=2.00E+10, J=0.133, Iy=0.213, Iz=0.259, Ay=0.233, Az=0.58)
    slab_section = og.Section(A=0.04428, E=3.47E+10, G=2.00E+10, J=2.6e-4, Iy=1.1e-4, Iz=2.42e-4,
                           Ay=3.69e-1, Az=3.69e-1, unit_width=True)
    exterior_I_beam_section = og.Section(A=0.044625, E=3.47E+10, G=2.00E+10, J=2.28e-3, Iy=2.23e-1, Iz=1.2e-3,
                                      Ay=3.72e-2, Az=3.72e-2)

    # define grillage members
    I_beam = og.GrillageMember(member_name="Intermediate I-beams", section=I_beam_section, material=concrete)
    slab = og.GrillageMember(member_name="concrete slab", section=slab_section, material=concrete)
    exterior_I_beam = og.GrillageMember(member_name="exterior I beams", section=exterior_I_beam_section, material=concrete)
    example_bridge = og.OpsGrillage(bridge_name="SuperT_10m", long_dim=10, width=7, skew=[42, 0],
                                 num_long_grid=7, num_trans_grid=5, edge_beam_dist=1, mesh_type="Ortho")

    # set grillage member to element groups of grillage model
    example_bridge.set_member(I_beam, member="interior_main_beam")
    example_bridge.set_member(exterior_I_beam, member="exterior_main_beam_1")
    example_bridge.set_member(exterior_I_beam, member="exterior_main_beam_2")
    example_bridge.set_member(exterior_I_beam, member="edge_beam")
    example_bridge.set_member(slab, member="transverse_slab")
    example_bridge.set_member(exterior_I_beam, member="start_edge")
    example_bridge.set_member(exterior_I_beam, member="end_edge")


    example_bridge.create_ops(pyfile=False)
    og.opsplt.plot_model("nodes")


..  figure:: ../../images/42_0_mesh.png
    :align: center
    :scale: 75 %

    Figure 2: Grillage model of the exemplar 28 m bridge.