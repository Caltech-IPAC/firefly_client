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


