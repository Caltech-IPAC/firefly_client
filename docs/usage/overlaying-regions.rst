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
