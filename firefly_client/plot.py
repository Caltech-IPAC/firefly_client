
"""
`firefly_client.plot` is a state-base interface to firefly_client,
inspired by `matplotlib.pyplot`.
"""

import logging
import os
#import sys
import tempfile
import time
#import urllib
#from astropy.io import fits
#from ws4py.client import HandshakeError
from .firefly_client import FireflyClient

logger = logging.getLogger(__name__)

fc = None

for c in FireflyClient.get_instances():
    _ = c()
    if _ and _._is_page_connected():
        fc = _
        break

public_urls = ['https://lsst-demo.ncsa.illinois.edu/firefly',
               'https://irsa.ipac.caltech.edu/irsaviewer']

try_urls = []
html_file = 'slate.html'
last_tblid = None

if 'FIREFLY_URL' in os.environ:
    try_urls.append(os.environ['FIREFLY_URL'])
if 'FIREFLY_HTML' in os.environ:
    html_file = os.environ['FIREFLY_HTML']

try_urls.append('http://localhost:8080/firefly')
try_urls.append('http://127.0.0.1:8080/firefly')

try_urls += public_urls

if fc is None:
    for url in try_urls:
        try:
            logger.debug('attempting to connect to {}'.format(url))
            fc = FireflyClient(url, html_file=html_file)
            break
        except Exception:
            logger.debug('connection failed to {}'.format(url))

if fc is None:
    raise RuntimeError('Cannot find existing FireflyClient or valid server URL')

#if not fc._is_page_connected():
#    fc.launch_browser()

# Set up default cells
time.sleep(2)
table_cellid = 'tables'
plots_cellid = 'plots'
images_cellid = 'images'

def use_client(ffclient):
    global fc
    fc = ffclient
    if not fc._is_page_connected():
        open_browser()

def reset_layout():
    fc.add_cell(row=0, col=0, width=2, height=2, element_type='tables',
            cell_id=table_cellid)
    fc.add_cell(row=2, col=0, width=1, height=2, element_type='xyPlots',
            cell_id=plots_cellid)
    fc.add_cell(row=2, col=1, width=1, height=2, element_type='images',
            cell_id=images_cellid)

def reset_server(url, channel=None, html_file=html_file):
    global fc
    fc = FireflyClient(url, channel=channel, html_file=html_file)

def display_url():
    fc.display_url()

def open_browser():
    fc.launch_browser()

def clear():
    fc.reinit_viewer()


def scatter(x_col, y_col, tbl_id='', size=4, color=None, marker=None,
            title='', xlabel=None, ylabel=None, cell_id=plots_cellid, **kwargs):
    """Make a scatter plot from a table uploaded to Firefly

    Parameters:
    -----------
    x_col: `str`
        name of column to use for x-axis data
    y_col: `str`
        name of column to use for y-axis data
    tbl_id: `str`
        Firefly table ID. If empty, use the ID of the last uploaded table
    size: `int`
        marker size. Defaults to 4.
    color: `str`
        marker color. None uses the Plotly default
    marker: `str`
        marker style. None uses the Plotly default
    title: `str`
        plot title. Defaults to empty string
    xlabel: `str`
        x-axis label. If None, defaults to xname
    ylabel: `str`
        y-axis label. If None, defaults to yname
    cell_id: `str`
        ID of Slate cell from add_cell, defaults to table_cellid


    """
    layout = dict(xaxis=dict(title=xlabel if xlabel else x_col),
                  yaxis=dict(title=ylabel if ylabel else y_col))
    if title is not None:
        layout['title'] = title
    if len(tbl_id) == 0:
        logger.debug('Using last_tblid: {}'.format(last_tblid))
        tbl_id = last_tblid
    trace = dict(tbl_id=tbl_id,
                x = 'tables::' + x_col,
                y = 'tables::' + y_col,
                mode = 'markers',
                type = 'scatter',
                marker = dict(size=size))
    trace.update(kwargs)
    fc.show_chart(layout=layout, data=[trace], group_id=cell_id)


def hist(data_col, tbl_id='', nbins=30, title='', xlabel=None,
         ylabel=None, cell_id=plots_cellid, **kwargs):
    """Make a histogram from a table uploaded to Firefly

    data_col: `str`
        data column name or expression
    tbl_id: `str`
        Firefly table ID. If empty, use the ID of the last uploaded table
    nbins: `int`
        number of bins to use for histogram. Default 30
    title: `str`
        plot title. Defaults to empty string
    xlabel: `str`
        x-axis label. If None, defaults to xname
    ylabel: `str`
        y-axis label. If None, defaults to yname
    cell_id: `str`
        ID of Slate cell from add_cell, defaults to table_cellid
    """
    layout = dict(xaxis=dict(title=xlabel if xlabel else data_col),
                  yaxis=dict(title=ylabel if ylabel else 'Number'))
    if title is not None:
        layout['title'] = title
    if len(tbl_id) == 0:
        logger.debug('Using last_tblid: {}'.format(last_tblid))
        tbl_id = last_tblid
    hist_data = dict(
        type='fireflyHistogram',
        name=data_col,
        marker={'color': 'rgba(153, 51, 153, 0.8)'},
        firefly=dict(
            tbl_id=tbl_id,
            options=dict(
                algorithm='fixedSizeBins',
                fixedBinSizeSelection='numBins',
                numBins=nbins,
                columnOrExpr=data_col
            )
        )
    )
    hist_data.update(kwargs)
    fc.show_chart(group_id=cell_id, layout=layout, data=[hist_data] )
    return

def upload_table(table, title=None, show=True, write_func="auto", tbl_index=1, page_size=200):
    """upload a table object to Firefly

    Parameters:
    -----------
    table: `str` or table-like object
        path to table file, or table object to upload
    title: `str`
        title of the table, also used as the table ID, if specified. Otherwise auto-generated.
    show: `bool`
        display the table in a table viewer in the browser. default True.
    write_func: `str` or function
        function for serializing the table. If 'auto', try to auto-discover the write method
        from the type of the table object and known table types.
    tbl_index: `int`
        If the table object contains multiple tables, use the first one.
    page_size: `int`
        Number of rows in each page of the table viewer. Default 200.

    Returns:
    --------
    tbl_id: `str`
        Table ID on the Firefly server
    """
    if isinstance(table, str):
        tval = fc.upload_file(table)
    else:
        if write_func == 'auto':
            if 'lsst.afw.table' in str(type(table)):
                write_func = table.writeFits
            elif 'astropy.table.table.Table' in str(type(table)):
                def write_astropy(fname):
                    atable = table.copy()
                    for c in atable.colnames:
                        if len(c) > 68:
                            atable.rename_column(c, c[:68])
                    #atable.remove_columns([c for c in table.colnames if len(c) > 68])
                    import warnings
                    with warnings.catch_warnings():
                        warnings.simplefilter('ignore', UserWarning)
                        atable.write(fname, format='fits', overwrite=True)
                write_func = write_astropy
            else:
                raise RuntimeError('Unable to auto-discover output method for ' + str(type(table)))
        with tempfile.NamedTemporaryFile(delete=False, suffix='.fits') as fd:
            write_func(fd.name)
        tval = fc.upload_file(fd.name)
        logger.debug('Image name is {}'.format(fd.name))
        os.remove(fd.name)
    if title is None:
        tbl_id = FireflyClient._gen_item_id('Table')
    else:
        tbl_id = title
    if show:
        status = fc.show_table(tval, tbl_id=tbl_id, title=title, table_index=tbl_index, page_size=page_size)
    else:
        status = fc.fetch_table(tval, tbl_id=tbl_id, table_index=tbl_index, page_size=page_size)
    if status['success']:
        global last_tblid
        last_tblid = tbl_id
        return tbl_id
    else:
        raise RuntimeError('table upload unsuccessful')



def upload_image(image, title=None, write_func='auto', cell_id=images_cellid):
    """display an array or astropy.io.fits HDU or HDUList

    Parameters:
    -----------
    data: 2-D numpy array, or FITS object with write method
        Data to show in Firefly
    title: `str`
        title for the plot, if None then an integer is used

    Returns:
    --------
    image_id: `str`
        Image ID on the Firefly server
    """
    if isinstance(image, str):
        fval = fc.upload_file(image)
    else:
        if write_func == 'auto':
            if 'lsst.afw.image' in str(type(image)):
                write_func = image.writeFits
            elif 'astropy.io.fits' in str(type(image)):
                def write_astropy_image(fname):
                    import warnings
                    with warnings.catch_warnings():
                        warnings.simplefilter('ignore', UserWarning)
                        image.writeto(fname, overwrite=True)
                write_func = write_astropy_image
            elif 'numpy.ndarray' in str(type(image)):
                import astropy.io.fits
                hdu = astropy.io.fits.PrimaryHDU(data=image)
                write_func = lambda fname: hdu.writeto(fname, overwrite=True)
            else:
                raise RuntimeError('Unable to auto-discover output method for ' + str(type(table)))
        with tempfile.NamedTemporaryFile(delete=False, suffix='.fits') as fd:
            write_func(fd.name)
        fval = fc.upload_file(fd.name)
        logger.debug('Image name is {}'.format(fd.name))
        os.remove(fd.name)
    if title is None:
        image_id = FireflyClient._gen_item_id('Image')
        title=image_id
    else:
        image_id = title
    status = fc.show_fits(fval, plot_id=image_id, title=title, viewer_id=cell_id)
    if status['success']:
        global last_imageid
        last_imageid = image_id
        return image_id
    else:
        raise RuntimeError('image upload and display unsuccessful')
