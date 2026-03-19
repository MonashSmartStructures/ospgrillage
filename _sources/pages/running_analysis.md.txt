# Running an analysis

For all example code on this page, *ospgrillage* is imported as `og`

```python
import ospgrillage as og
```

## Analyse load cases

Once all defined load cases (static and moving) have been added to the grillage object, analysis can be conducted.

To analyse load case(s), call {meth}`~ospgrillage.osp_grillage.OspGrillage.analyze`. By default this runs all defined load cases. To run only specific load cases, pass a load case name `str` or a `list` of names to the `load_case` keyword argument. The following example shows the various options:

```python
# analyze all
example_bridge.analyze()
# or a single str
example_bridge.analyze(load_case="DL")
# or a single element list
example_bridge.analyze(load_case=["DL"])
# or a list of multiple load cases
example_bridge.analyze(load_case=["DL","SDL"])
```

## Querying the model

### Nodes

Use {meth}`~ospgrillage.osp_grillage.OspGrillage.get_nodes` to retrieve node
information from the model.

### Elements

Use {meth}`~ospgrillage.osp_grillage.OspGrillage.get_element` to query element
properties and tags from the model.
