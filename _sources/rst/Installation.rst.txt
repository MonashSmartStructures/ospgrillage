========================
Installation
========================

Required dependencies
----------------------

* Python (3.8 or later)
* Openseespy (3.3 or later)
* numpy
* xarray


Instructions
--------------------
The easiest way to install is to use python package index `pip`.

.. code-block:: python

    pip install ospgrillage

For users wishing to develop/contribute, install as follows:

.. code-block:: python

    git clone https://github.com/MonashSmartStructures/ospgrillage.git
    cd ospgrillage
    pip setup.py install -e


Installing dependencies
------------------------

Dependencies are automatically installed when using :code:`pip`.
The dependencies can be seen in the *setup.cfg* file in the project repository.

Tests
-------------------
The module comes with a ``pytest`` protocol for each sub module ``py`` file, which users can run ``pytest`` in the root directory of the module
to tests all modules.

.. code-block:: python

    python -m pytest

