.. currentmodule:: firefly_client

.. _firefly_client:

#####################################################
firefly\_client - Python API to Firefly visualization
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


.. _firefly_client-prerequisites:

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
    fc = FireflyClient('irsa.ipac.caltech.edu:80', basedir='irsaviewer')

Third, open a new browser tab using the :meth:`FireflyClient.launch_browser` method:

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

Fifth, display a table by uloading a catalog table (here, in IPAC format) and
then showing the table. The sources are also overlaid automatically on the
image since the catalog contains celestial coordinates, and a default
chart is displayed.

.. code-block:: py
    :name: gs-table

    tval = fc.upload_file('m31-2mass-2412-row.tbl')
    fc.show_table(tval)

.. _firefly_client-using:

Using firefly_client
====================

The `firefly_client` package contains the class `FireflyClient` which
provides the Python API to Firefly.

Initializing a FireflyClient instance
-------------------------------------

Once a Firefly server has been identified, the connection parameters can be
used to initialize a :class:`FireflyClient` instance. A `host:port` parameter is
required. Optional arguments are `channel` and `basedir`.

For a default server running locally, use `localhost` or `127.0.0.1` together
with the port that the server is using. The default port is 8080.

.. code-block:: py
    :name: using-localhost

    import firefly_client
    fc = firefly_client.FireflyClient('127.0.0.1:8080')

If the Python session is running on your own machine, you can use the
:meth:`FireflyClient.launch_browser` method to open up a browser tab.

.. code-block:: py
    :name: launch-browser

    fc.launch_browser()

The :meth:`FireflyClient.launch_browser` method will return the channel string. If the user
did not specify a channel string, the Firefly server will auto-generate one.

.. warning::

    On Mac OS X 10.12.5, an error message may be displayed with a URL and
    a note that it doesn't understand the "open location message". If a
    browser tab is not automatically opened, copy and paste the displayed
    URL into the address bar of your browser. This issue has been fixed
    in Mac OS X 10.12.6.

If your Python session is not running on your local machine, the
:meth:`FireflyClient.launch_browser`
method should not be used. Instead, display the URL to which you must connect
using :meth:`FireflyClient.get_firefly_url`:

.. code-block:: py

    print(fc.get_firefly_url('full'))

Copy and paste the string into  your address bar. If you are using SSH
tunneling to connect to your Firefly server, you may need to modify
the host and port parts of the URL to match your tunnel.

You may set the `channel` parameter to a string of your choosing. In general,
care should be taken to make the channel unique -- otherwise other users
of your Firefly server could write to your display.

.. code-block:: py

    fc = firefly_client.FireflyClient('127.0.0.1:8080', channel='qxefvt')

Some Firefly servers do not use the default `basedir` in their URLs. Other
values in use include `suit` (for LSST) and `irsaviewer` (for applications
deployed for the Infrared Science Archive). A public server is usually available
at `http://irsaviewer.ipac.caltech.edu:80/irsaviewer <http://irsaviewer.ipac.caltech.edu:80/irsaviewer>`:

.. code-block:: py

    fc = firefly_client.FireflyClient('irsa.ipac.caltech.edu:80', basedir='irsaviewer')

.. warning::

    After initializing :class:`FireflyClient`, make sure you have opened a web browser
    to the appropriate URL, before proceeding to use the Python API described
    in the following sections.

Displaying Images
-----------------

Since Firefly was originally developed to visualize data products from
astronomical archives, displaying an image is a two-step process of
uploading a file and then showing it. The examples here use the data
products downloaded in :ref:`firefly_client-getting-started`.

The :meth:`FireflyClient.upload_file` method uploads the file and
returns a location understood by the Firefly server. The location
string is passed to :meth:`FireflyClient.show_fits` to display
the image. In the display step,
it is recommended to explicitly specify the `plot_id` parameter
for later use in modifying the image display.

.. code-block:: py

    fval = fc.upload_file('2mass-m31-green.fits')
    fc.show_fits(fval, plot_id='m31-green', title='2MASS H, M31')


Modifying an Image Display
--------------------------

Zooming, panning, and changing the stretch (mapping of pixels to display
values) is accomplished by corresponding methods, passing in the `plot_id`
as the first argument.

.. code-block:: py

    fc.set_zoom('m31-green', 4)
    fc.set_pan('m31-green', 200, 195)
    fc.set_stretch('m31-green', 'sigma', 'log', lower_value=-2, upper_value=30)

A "zscale" stretch may be commanded with alternate parameters:

.. code-block:: py

    fc.set_stretch('m31-green', 'zscale', 'linear')

At present the API does not include a function for changing the color map
for the image. The relevant Javascript action may be invoked using
:meth:`FireflyClient.dispatch_remote_action`:

.. code-block:: py

    fc.dispatch_remote_action(fc.channel,
        action_type='ImagePlotCntlr.ColorChange',
        payload={'plotId': 'm31-green',
                 'cbarId': 16})

The colormap can be reverted to the original grayscale by using the
command above together with `'cbarId' : 0`.

Visualizing Regions
-------------------

The API includes detailed support for ds9-style regions. A list of strings
containing region commands can be added to an overlay layer on an image.

.. code-block:: py

    region_data = ['J2000',
                   'text 10.6845417 41.2689167{M31 Nucleus} #color=red',
                   'point 10.7035000 41.2535833 # point=circle 20',
                   'image;line(249.5 164.1 283.8 206.6) # color=blue width=5']
    fc.add_region_data(region_data=region_data, region_layer_id='layer1',
                       title='my_marks', plot_id='m31-green')

An individual region command can be removed using
:meth:`FireflyClient.remove_region_data`. To remove the blue line:

.. code-block:: py

    fc.remove_region_data(region_data=region_data[-1],
                          region_layer_id='layer1')

An entire region layer can be deleted with :meth:`FireflyClient.delete_region_layer`:

.. code-block:: py

    fc.delete_region_layer(region_layer_id='layer1', plot_id='m31-green')

A region layer can be uploaded from a file and overlaid on an image by
using :meth:`FireflyClient.upload_file` and :meth:`FireflyClient.overlay_region_layer`:

.. code-block:: py

    with open('myreg.txt', 'w') as fh:
        fh.write('\n'.join(region_data))
    rval = fc.upload_file('myreg.txt')
    fc.overlay_region_layer(file_on_server=rval,
                            region_layer_id='layer2',
                            plot_id='m31-green')


Visualizing Tables and Catalogs
-------------------------------

Tables can be uploaded to the Firefly server with :meth:`FireflyClient.upload_file`,
and displayed in a table viewer component with :meth:`FireflyClient.show_table`.
The default is to overlay symbols for each row of the table (`is_catalog=True`)
if the table contains recognizable celestial coordinates.

.. code-block:: py

    tval = fc.upload_file('m31-2mass-2412-row.tbl')
    fc.show_table(file_on_server=tval, tbl_id='m31-table')

If it is desired to overlay the table on an image, or to make plots from it,
without showing the table in the viewer, use :meth:`FireflyClient.fetch_table`:

.. code-block:: py

    fc.fetch_table(file_on_server=tval, tbl_id='invisible-table')

If the table does not contain celestial coordinates recognized by Firefly,
the image overlay will not appear. BUt if you specifically do not want
the table overlaid on the image, `is_catalog=False` can be specified:

.. code-block:: py

    fc.show_table(file_on_server=tval, tbl_id='2mass-tbl', is_catalog=False)

Making Plots and Histograms
---------------------------

Once a table has been uploaded to Firefly, :meth:`FireflyClient.show_xyplot`
will display a scatter plot. The `xCol` and `yCol` parameters can be set
to names of columns in the table, or to arithmetic expressions that combine
table columns.

.. code-block:: py

    fc.show_xyplot(tbl_id='2mass-tbl', xCol='j_m', yCol='h_m - k_m')

A histogram can be displayed with :meth:`FireflyClient.show_histogram`:

.. code-block:: py

    fc.show_histogram(tbl_id='2mass-tbl', col='j_m')

Both plot types include options for log scaling as well as other settings.


Advanced: Callbacks and Extensions
----------------------------------

Callback functions can be added to :class:`FireflyClient`. Here is a simple
example of defining and registering a callback that prints world coordinates
to the Python session:

.. code-block:: py

    def print_coords(event):
        if 'wpt' in event['data']:
           wpt = event['data']['wpt']
           wdata = wpt.split(';')
           ra = float(wdata[0])
           dec = float(wdata[1])
           print('ra={:.6f}, dec={:.6f}'.format(ra,dec))

    plistner = fc.add_listener(print_coords)

To activate the callback in point-selection mode, add it as an extension
with `ext_type='POINT'`. By default, the title of the extension will appear
as a clickable icon when the Firefly viewer is in point mode. A small image
can be passed in instead via the `img_src` parameter.

.. code-block:: py

    fc.add_extension(ext_type='POINT', plot_id=None, title='Print coords',
                     extension_id='pickit')

To activate point-selection mode, in the Firefly browser tab, select
the 'Lock by click' checkbox at the upper right. Then selecting any point
in an image will overlay a box at that point. Finally, click on the
'Print coords' icon in the image display window to cause the callback
to be triggered, and coordinates to be printed out.

The callback can be deleted with `FireflyClient.remove_listener`:

.. code-block:: py

    fc.remove_listener(plistner)



Python API reference
====================

.. automodapi:: firefly_client
	 :no-inheritance-diagram:

