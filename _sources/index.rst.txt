.. currentmodule:: firefly_client

.. _firefly_client:

#####################################################
firefly_client - Python API to Firefly visualization
#####################################################

`firefly_client`  provides a Python API to the Firefly visualization framework.
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

The `firefly_client` package provides a lightweight client class that includes
a Python interface to `Firefly's Javascript API <http://firefly.lsst.io>`_.
This document contains examples of how to start a `FireflyClient` instance
with details about the server location, and how to use the instance
to upload and display astronomical images, tables and catalogs.


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

