#################
Local development
#################

Get latest source from ``master`` branch at https://github.com/Caltech-IPAC/firefly_client.


Environment Setup
-----------------

TBD


Building documentation
----------------------

Make sure you have the virtual/conda environment activated and documentation
dependencies installed in that environment.

Then do:

.. code-block:: shell

    cd docs
    make clean && make html

Open ``docs/_build/html/index.html`` in your browser to see the documentation
website. 

Each time you make a change in documentation source, build it using 
above command and reload the above file in browser.