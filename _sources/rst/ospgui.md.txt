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

## API reference

### Main window

```{autoclass} ospgrillage.ospgui.BridgeAnalysisGUI
:members:
:show-inheritance:
```

### Input widget

```{autoclass} ospgrillage.ospgui.BridgeInputWidget
:members:
:show-inheritance:
```
