# GUI — ospgui

The *ospgui* module provides a graphical interface for building *ospgrillage*
bridge deck models interactively, without writing Python code.

## Installation

The GUI depends on PyQt5, which is an optional extra:

```bash
pip install "ospgrillage[gui]"
```

## Launching

From the command line:

```bash
ospgui
```

Or from within Python:

```python
from ospgrillage.ospgui import main
main()
```

## Interface overview

The window is divided into three panels:

- **Left** — tabbed input forms for geometry, materials, sections, and members
  (provided by `BridgeInputWidget`).
- **Centre** — a live code view showing the generated *ospgrillage* Python source,
  updated as parameters change.
- **Right** — a 3-D mesh preview rendered via *vfo*.

## API reference

```{autofunction} ospgrillage.ospgui.main
```
