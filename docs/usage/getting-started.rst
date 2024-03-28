###############
Getting Started
###############

Prerequisites
=============

* Python 3

* firefly_client (installable with `pip install firefly_client`)

* URL for a Firefly server

.. _firefly_client-getting-started:

Getting Started
===============

First, download some data by using wget or curl:

.. code-block:: shell
   :name: gs-download

   wget http://web.ipac.caltech.edu/staff/roby/demo/2mass-m31-green.fits
   wget http://web.ipac.caltech.edu/staff/roby/demo/m31-2mass-2412-row.tbl

   curl -o 2mass-m31-green.fits http://web.ipac.caltech.edu/staff/roby/demo/2mass-m31-green.fits
   curl -o m31-2mass-2412-row.tbl http://web.ipac.caltech.edu/staff/roby/demo/m31-2mass-2412-row.tbl

Second, start a Python session and connect an instance of :class:`firefly_client.FireflyClient`
to a Firefly server. In this example, we use a public server. For ease of demonstration,
please start the Python session in the directory from which you downloaded the sample files.

.. code-block:: py
    :name: gs-start

    from firefly_client import FireflyClient
    fc = FireflyClient.make_client('https://irsa.ipac.caltech.edu/irsaviewer')

Third, open a new browser tab using the :meth:`FireflyClient.launch_browser` method. If
a browser cannot be opened, a URL will be displayed for your web browser.

.. code-block:: py
    :name: gs-launch

    fc.launch_browser()

Fourth, display an image in a FITS file by uploading the
file to the server with :meth:`FireflyClient.upload_file`
and then showing the image.

.. code-block:: py
    :name: gs-image

    fval = fc.upload_file('2mass-m31-green.fits')
    fc.show_fits(fval)

Fifth, display a table by uploading a catalog table (here, in IPAC format) and
then showing the table. The sources are also overlaid automatically on the
image since the catalog contains celestial coordinates, and a default
chart is displayed.

.. code-block:: py
    :name: gs-table

    tval = fc.upload_file('m31-2mass-2412-row.tbl')
    fc.show_table(tval)
