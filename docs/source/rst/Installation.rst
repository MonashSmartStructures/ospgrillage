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

For development, install as follows:

.. code-block:: python

    git clone https://github.com/MonashSmartStructures/ops-grillage.git
    cd ops-grillage
    pip install -e



Installing dependencies
------------------------

The *ospgrillage* module uses several external modules for its usage. A list of modules required for the working
environment of *ospgrillage* is found in the *requirement.txt* file.

To install a working environment with all required dependencies, run the following command line in terminal

.. code-block:: python

    pip install -r /path/to/requirements.txt


Tests
-------------------
The module comes with a pytest protocol named `test_file.py` which users can run `pytest` in the root directory of the module.

.. code-block:: python

    python -m pytest

