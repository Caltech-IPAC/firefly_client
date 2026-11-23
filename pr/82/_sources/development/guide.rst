#################
Local development
#################

Get latest source from ``master`` branch at https://github.com/Caltech-IPAC/firefly_client.

.. code-block:: shell

    git clone https://github.com/Caltech-IPAC/firefly_client.git
    cd firefly_client


Environment Setup
-----------------

Create a Python virtual environment and install required dependencies.
The folllowing commands demonstrate how to do this using ``conda`` (assuming you have `miniconda <https://www.anaconda.com/docs/getting-started/miniconda/>`_ installed on your system):

.. code-block:: shell

    conda create -n ffpy -c conda-forge python jupyter astropy # jupyter and astropy are needed for running examples
    conda activate ffpy
    pip install -e ".[tests,docs]" # editable installation with tests and docs dependencies


Now you can run the examples notebooks/scripts in the ``examples/`` directory.
This can be done by starting a Jupyter Notebook or JupyterLab session from the terminal (``jupyter notebook`` or ``jupyter lab``), or by using an IDE that supports running Python notebooks or scripts (like VSCode, IntelliJ, etc.).

.. note::
    The changes you make to the source code will be reflected when you run the examples since the package is installed in editable mode.
    But make sure to restart the active Python kernel/session to pick up the changes.

Building documentation
----------------------

Make sure you have the virtual environment activated and documentation
dependencies installed in that environment (``[docs]``).

Then do:

.. code-block:: shell

    cd docs
    make clean && make html

Open ``docs/_build/html/index.html`` in your browser to see the documentation
website. 

Each time you make a change in documentation source, build it using 
above command and reload the above html file in browser.

.. note::
    The Sphinx docs include rendered Jupyter notebooks (via ``nbsphinx``), which can require **pandoc**.
    If you see an error like ``PandocMissing``, install pandoc first (e.g., ``brew install pandoc`` on macOS).

Unit Tests
----------

Unit tests live in the ``tests/`` directory and use ``pytest``.
Make sure you have the virtual environment activated with test dependencies installed (``[tests]``), then run:

.. code-block:: shell

    pytest tests/

Development Tests/Examples
--------------------------

The ``examples/development_tests/`` directory contains notebooks for manually testing behaviour that requires a live Firefly server.
Refer to the `examples/development_tests directory <https://github.com/Caltech-IPAC/firefly_client/tree/master/examples/development_tests>`_ of the firefly_client GitHub repository.
