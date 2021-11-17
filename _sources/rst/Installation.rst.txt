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

For users wishing to use jupyter notebook, install as follows:

.. code-block:: python

    1. pip install --user virtualenv
    1.1 python -m venv ospg
    2. Activate virtual env ospg\bin\activate
    3. python -m pip install jupyterlab
    4. pip install ipykernel
    5. ipython kernel install --name "opsg" --user
    6. pip install ospgrillage
    7. jupyter-lab

The following instructions are for jupyter notebook but with virtual environment created via `conda`:

.. code-block:: python

    1. Create a new environment: conda create --name ospg python=3.9
    2. Now activate the new env: conda activate ospg
    3. Install jupyter-lab: conda install -c conda-forge jupyterlab
    4. Install the kernels for linking with jupyter: pip install ipykernel followed by: ipython kernel install --name "opsg" --user
    5. Install ospgrillage: pip install ospgrillage
    6. And run in the new env: jupyter-lab

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

