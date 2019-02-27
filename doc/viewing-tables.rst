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

