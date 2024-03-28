Making Plots and Histograms
---------------------------

Once a table has been uploaded to Firefly, :meth:`FireflyClient.show_chart`
will display a scatter plot. The `x` and `y` parameters can be set
to use names of columns in the table, or to arithmetic expressions that combine
table columns.

.. code-block:: py

   trace1 = dict(tbl_id='2mass-tbl', x='tables::j_m',
                 y='tables::h_m-k_m', mode='markers', type='scatter',
                 marker=dict(size=4))

    layout1 = dict(title='2MASS color-mag',
                   xaxis=dict(title='J'), yaxis=dict(title='H - K'))

    fc.show_chart(layout=layout1, data=[trace1])

A histogram can be displayed with :meth:`FireflyClient.show_chart`:

.. code-block:: py

    trace2 = dict(type='fireflyHistogram',
                  name='j_m',
                  marker=dict(color='rgba(153, 51, 153, 0.8)'),
                  firefly=dict(tbl_id='2mass-tbl',
                               options=dict(algorithm='fixedsizeBins',
                                            fixedBinSizeSelection='numBins',
                                            numBins=30,
                                            columnOrExpr='j_m')))

    layout_hist = dict(title='Photometry histogram',
                     xaxis=dict(title='j_m (mag)'),
                     yaxis=dict(title='Number'))

    fc.show_chart(layout=layout_hist, data=[trace2])

Both plot types include options for log scaling as well as other settings.
