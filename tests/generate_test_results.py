"""Generate test NetCDF results files for GUI testing.

Produces one ``.nc`` file per model/mesh type in the current working
directory.  Each file contains two static load cases (Dead Load + Overlay)
and is self-contained (node coordinates and member mappings embedded) so
it can be opened directly in ``ospgui``.

Model types generated:

- **beam** (default): Oblique and Ortho mesh variants (skewed)
- **beam_link**: Beam-link model with rigid-link offsets
- **shell_beam**: Shell-beam hybrid model

Usage::

    python tests/generate_test_results.py

The ``.nc`` files are **not** committed to the repository — regenerate
them locally whenever the results format changes.
"""

import ospgrillage as og

# -- Units -----------------------------------------------------------------
kilo, milli, N, m = 1e3, 1e-3, 1, 1
mm = milli * m
m2, m3, m4 = m**2, m**3, m**4
kN = kilo * N

# -- Common geometry -------------------------------------------------------
L = 10.0 * m
w = 7.0 * m


# -- Materials & sections --------------------------------------------------
concrete = og.create_material(material="concrete", code="AS5100-2017", grade="65MPa")
concrete_shell = og.create_material(
    material="concrete", code="AS5100-2017", grade="50MPa", rho=2400
)

long_sec = og.create_section(
    A=0.034 * m2,
    J=2.08e-3 * m3,
    Iz=6.77e-3 * m4,
    Iy=2.04e-3 * m4,
    Az=6.10e-3 * m2,
    Ay=3.99e-3 * m2,
)
edge_sec = og.create_section(
    A=0.034 * m2,
    J=2.08e-3 * m3,
    Iz=6.77e-3 * m4,
    Iy=2.04e-3 * m4,
    Az=6.10e-3 * m2,
    Ay=3.99e-3 * m2,
)
trans_sec = og.create_section(
    A=0.504 * m2,
    J=5.22303e-3 * m3,
    Iy=0.32928 * m4,
    Iz=1.3608e-3 * m4,
    Ay=0.42 * m2,
    Az=0.42 * m2,
    unit_width=True,
)
end_sec = og.create_section(
    A=0.504 / 2 * m2,
    J=2.5e-3 * m3,
    Iy=2.73e-2 * m4,
    Iz=6.8e-4 * m4,
    Ay=0.21 * m2,
    Az=0.21 * m2,
    unit_width=True,
)
shell_sec = og.create_section(h=0.2)

long_beam = og.create_member(section=long_sec, material=concrete)
edge_beam_mem = og.create_member(section=edge_sec, material=concrete)
trans_slab = og.create_member(section=trans_sec, material=concrete)
end_slab = og.create_member(section=end_sec, material=concrete)
slab_shell = og.create_member(section=shell_sec, material=concrete_shell)


def _assign_beam_members(model):
    """Set all member types on a beam-type model."""
    model.set_member(long_beam, member="interior_main_beam")
    model.set_member(long_beam, member="exterior_main_beam_1")
    model.set_member(long_beam, member="exterior_main_beam_2")
    model.set_member(edge_beam_mem, member="edge_beam")
    model.set_member(trans_slab, member="transverse_slab")
    model.set_member(end_slab, member="start_edge")
    model.set_member(end_slab, member="end_edge")


def _assign_shell_members(model):
    """Set members on a shell_beam model."""
    model.set_member(long_beam, member="interior_main_beam")
    model.set_member(long_beam, member="exterior_main_beam_1")
    model.set_member(long_beam, member="exterior_main_beam_2")
    model.set_shell_members(slab_shell)


def _add_loads(model):
    """Add Dead Load and Overlay load cases."""
    DL = og.create_load_case(name="Dead Load")
    for z_pos in model.Mesh_obj.noz[1:-1]:
        p1 = og.create_load_vertex(x=0, z=z_pos, p=22.4 * kN / m)
        p2 = og.create_load_vertex(x=L, z=z_pos, p=22.4 * kN / m)
        DL.add_load(og.create_load(loadtype="line", point1=p1, point2=p2, name="SW"))
    model.add_load_case(DL)

    overlay = og.create_load(
        loadtype="patch",
        name="overlay",
        point1=og.create_load_vertex(x=0, z=0, p=4.32 * kN / m**2),
        point2=og.create_load_vertex(x=L, z=0, p=4.32 * kN / m**2),
        point3=og.create_load_vertex(x=L, z=w, p=4.32 * kN / m**2),
        point4=og.create_load_vertex(x=0, z=w, p=4.32 * kN / m**2),
    )
    OL = og.create_load_case(name="Overlay")
    OL.add_load(overlay)
    model.add_load_case(OL)


# -- Model definitions -----------------------------------------------------
# Each entry: (filename, create_grillage kwargs, member assignment function)
MODELS = [
    # Beam models — two mesh types
    (
        "test_beam_oblique.nc",
        dict(
            bridge_name="Beam Oblique (skew 20)",
            long_dim=L,
            width=w,
            skew=20,
            num_long_grid=7,
            num_trans_grid=11,
            edge_beam_dist=1.0 * m,
            mesh_type="Oblique",
        ),
        _assign_beam_members,
    ),
    (
        "test_beam_ortho.nc",
        dict(
            bridge_name="Beam Ortho (skew 15)",
            long_dim=L,
            width=w,
            skew=15,
            num_long_grid=7,
            num_trans_grid=11,
            edge_beam_dist=1.0 * m,
            mesh_type="Ortho",
        ),
        _assign_beam_members,
    ),
    # Beam-link model — rigid-link offsets
    (
        "test_beam_link.nc",
        dict(
            bridge_name="Beam Link",
            long_dim=L,
            width=w,
            skew=-12,
            num_long_grid=7,
            num_trans_grid=5,
            edge_beam_dist=1.0 * m,
            mesh_type="Ortho",
            model_type="beam_link",
            beam_width=1.0,
            web_thick=0.02,
            centroid_dist_y=0.499,
        ),
        _assign_beam_members,
    ),
    # Shell-beam hybrid model
    (
        "test_shell_beam.nc",
        dict(
            bridge_name="Shell Beam",
            long_dim=L,
            width=w,
            skew=0,
            num_long_grid=7,
            num_trans_grid=11,
            edge_beam_dist=1.0 * m,
            mesh_type="Orth",
            model_type="shell_beam",
            max_mesh_size_z=1.0,
            max_mesh_size_x=1.0,
            offset_beam_y_dist=0.499,
            beam_width=0.89,
        ),
        _assign_shell_members,
    ),
]


def main():
    for filename, kwargs, assign_fn in MODELS:
        model_type = kwargs.get("model_type", "beam")
        mesh_type = kwargs.get("mesh_type", "?")
        skew = kwargs.get("skew", 0)
        print(
            f"Generating {filename} (type={model_type}, mesh={mesh_type}, skew={skew})..."
        )
        model = og.create_grillage(**kwargs)
        assign_fn(model)
        model.create_osp_model(pyfile=False)
        _add_loads(model)
        model.analyze()
        results = model.get_results(save_filename=filename)
        n_lc = len(results.coords["Loadcase"])
        print(f"  -> {n_lc} load cases, {len(results.data_vars)} variables")
    print("Done.")


if __name__ == "__main__":
    main()
