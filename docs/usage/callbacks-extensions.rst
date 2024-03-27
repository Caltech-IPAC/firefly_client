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

    fc.add_listener(print_coords)

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

    fc.remove_listener(print_coords)
