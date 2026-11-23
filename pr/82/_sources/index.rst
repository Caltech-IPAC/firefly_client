.. currentmodule:: firefly_client

.. _firefly_client:

#####################################################
firefly_client - Python API to Firefly visualization
#####################################################

``firefly_client`` provides a Python API to the Firefly visualization framework.
You can find it on Github at https://github.com/Caltech-IPAC/firefly_client

.. _firefly_client-intro:

Introduction
============

Firefly is a web framework for astronomical data access and visualization,
developed at Caltech/IPAC and deployed for the archives of several major
facilities including Spitzer, WISE, Plank and others. Firefly is the
framework for the Portal Aspect of the LSST Science User Platform.
Its client-server architecture is designed to enable a user to easily visualize
images and catalog data from a remote site.

The ``firefly_client`` package provides a lightweight client class that includes
a Python interface to Firefly's Javascript API.
This document contains examples of how to start a ``FireflyClient`` instance
with details about the server location, and how to use the instance
to upload and display astronomical images, tables and charts.


What to expect
==============

.. raw:: html

    <div style="margin-bottom: 1.15rem;">

.. image:: _static/firefly-in-python-flow.png
    :alt: Firefly in Python Flow Diagram
    :align: center

.. raw:: html

    </div>

It's important to note that Firefly visualization in Python notebooks is 
**NOT a per-cell chart or widget**, unlike common plotting libraries 
such as Plotly or Bokeh.

Under the hood, Firefly is a dedicated web application running at a specific 
URL, rather than a plot produced as a notebook cell output. 
Your notebook's Python session connects to a Firefly server, either a publicly 
hosted instance (such as the `IRSA Viewer`_) or a local server running via Docker_. 
Using a server enables advanced, compute-intensive interactivity that is 
difficult to support directly within a notebook's UI.

Multiple notebook cells can then send commands to the same Firefly instance, 
which manages linked views of images, charts, and tables, similar to an 
**interactive dashboard**.

.. _IRSA Viewer: https://irsa.ipac.caltech.edu/irsaviewer/
.. _Docker: https://hub.docker.com/r/ipac/firefly


.. _firefly_client-using:

Using firefly_client
====================

.. toctree::
    :maxdepth: 2

    Usage <usage/index>


.. _firefly_client-contributing:

Developer Guide
===============

.. toctree::
    :maxdepth: 2

    Development <development/index>


.. _firefly_client-pyapi:

Python API reference
====================

.. toctree::
    :maxdepth: 3

    API <reference>

