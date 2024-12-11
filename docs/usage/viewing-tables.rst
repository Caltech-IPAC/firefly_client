###############################
Visualizing Tables and Catalogs
###############################

Tables can be uploaded to the Firefly server with :meth:`FireflyClient.upload_file`,
and displayed in a table viewer component with :meth:`FireflyClient.show_table`.
The default is to overlay symbols for each row of the table (`is_catalog=True`)
if the table contains recognizable celestial coordinates.

.. code-block:: py

    tval = fc.upload_file('m31-2mass-2412-row.tbl')
    fc.show_table(file_on_server=tval, tbl_id='m31-table')

Modifying Table Display Parameters
----------------------------------

If it is desired to overlay the table on an image, or to make plots from it,
without showing the table in the viewer, use :meth:`FireflyClient.fetch_table`:

.. code-block:: py

    fc.fetch_table(file_on_server=tval, tbl_id='invisible-table')

Alternatively, you can turn off the `visible` parameter in :meth:`FireflyClient.show_table`:

.. code-block:: py

    fc.show_table(file_on_server=tval, tbl_id='invisible-table', visible=False)

If the table does not contain celestial coordinates recognized by Firefly,
the image overlay will not appear. But if you specifically do not want
the table overlaid on the image, `is_catalog=False` can be specified (it is 
`True` by default):

.. code-block:: py

    fc.show_table(file_on_server=tval, tbl_id='2mass-tbl', is_catalog=False)


Displaying Table from a URL
---------------------------

If you have the URL of a table, you can pass it directly instead of 
downloading it and then uploading it to firefly:

.. code-block:: py

    table_url = "http://irsa.ipac.caltech.edu/TAP/sync?FORMAT=IPAC_TABLE&QUERY=SELECT+*+FROM+fp_psc+WHERE+CONTAINS(POINT('J2000',ra,dec),CIRCLE('J2000',70.0,20.0,0.1))=1"
    tbl_id_2mass_psc = '2mass-point-source-catalog'
    fc.show_table(url=table_url, tbl_id=tbl_id_2mass_psc)

Filtering/Sorting a loaded Table
--------------------------------

After displaying a table in firefly, you can also apply filters on it. 
You will need to pass the `tbl_id` of that table and specify `filters` as an
SQL WHERE clause-like string with column names quoted:

.. code-block:: py
    
    fc.apply_table_filters(tbl_id=tbl_id_2mass_psc, filters='"j_m">15 and "j_m"<16 and "j_cmsig"<0.06')

You can sort the table by a column in ascending (`ASC`) or descending (`DESC`)
order:

.. code-block:: py
    
    fc.sort_table_column(tbl_id=tbl_id_2mass_psc, column_name='j_m', sort_direction='ASC')

If a column has sorting, it can be removed by specifying `sort_direction=''`.
