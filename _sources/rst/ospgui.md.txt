# ospgui — GUI geometry generator

The *ospgui* module provides a graphical user interface for building *ospgrillage*
bridge deck models interactively, without writing Python code.

## Launching the GUI

After installing with the `gui` extra (`pip install "ospgrillage[gui]"`), start the
GUI from the command line:

```bash
ospgui
```

or from within Python:

```python
from ospgrillage.ospgui import main
main()
```

```{note}
Automated API documentation for `ospgui` requires PyQt5 to be installed.
Install it with `pip install "ospgrillage[gui]"` before building the docs locally.
```
