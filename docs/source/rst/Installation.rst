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

    pip install git+https://github.com/MonashSmartStructures/ops-grillage.git

For users wishing to develop/contribute, install as follows:

.. code-block:: python

    git clone https://github.com/MonashSmartStructures/ospgrillage.git
    cd ospgrillage
    pip install -e



Installing dependencies
------------------------

A list of modules for a working python environment is found in the *requirement.txt* file.

To create a working environment with all required dependencies, run the following command line in terminal

.. code-block:: python

    pip install -r /path/to/requirements.txt


Tests
-------------------
The module comes with a pytest protocol for each sub module py file, which users can run `pytest` in the root directory of the module
to tests all modules.

.. code-block:: python

    python -m pytest

