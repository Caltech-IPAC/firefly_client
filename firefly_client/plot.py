"""
`firefly_client.plot` is a state-base interface to firefly_client,
inspired by `matplotlib.pyplot`.

Upon import, an existing FireflyClient instance will be used; then various
Firefly server URLs will be tried, starting with the value of the environment
variable FIREFLY_URL.
"""

import logging
import os
import tempfile
import time
from .firefly_client import FireflyClient
from .fc_utils import gen_item_id

logger = logging.getLogger(__name__)

fc = None
last_tblid = None
last_imageid = None
# Set up default cells
table_cellid = 'tables'
plots_cellid = 'plots'
images_cellid = 'images'


def use_client(ffclient):
    """Use the provided FireflyClient instance.

    This function will attempt to open a web browser for the viewer, if one
    is not already connected.

    Parameters:
    -----------
    ffclient : `firefly_client.FireflyClient`
        an instance of FireflyClient
    """
    global fc
    fc = ffclient


def _confirm_fc():
    if fc is None:
        raise ValueError('a FireflyClient instance has not been defined, define it first with use_client()')


def reset_layout():
    """Reset to the default layout

    The default layout is a table spanning the first row, and a second
    row containing plots in the first column and images in the second column.
    """
    _confirm_fc()
    fc.add_cell(row=0, col=0, width=2, height=2, element_type='tables', cell_id=table_cellid)
    fc.add_cell(row=2, col=0, width=1, height=2, element_type='xyPlots', cell_id=plots_cellid)
    fc.add_cell(row=2, col=1, width=1, height=2, element_type='images', cell_id=images_cellid)


def display_url():
    """Display the web viewer URL, if possible as a clickable link
    """
    _confirm_fc()
    fc.display_url()


def open_browser(force=False):
    """open a browser tab or window to the web viewer

    Parameters:
    -----------
    force : `bool`
        if True, open the browser even if one is already connected. Default False
    """
    _confirm_fc()
    fc.launch_browser(force=force)


def clear():
    """Clear the web viewer
    """
    _confirm_fc()
    fc.reinit_viewer()


def scatter(x_col, y_col, tbl_id='', size=4, color=None, alpha=1.0,
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
        Value can be 'blue' or 'rgb(50, 171, 96)'
    alpha: `float`
        marker opacity. Values should range between 0 and 1.
    title: `str`
        plot title. Defaults to empty string
    xlabel: `str`
        x-axis label. If None, defaults to x_col
    ylabel: `str`
        y-axis label. If None, defaults to y_col
    cell_id: `str`
        ID of Slate cell from add_cell, defaults to table_cellid


    """
    _confirm_fc()
    layout = dict(xaxis=dict(title=xlabel if xlabel else x_col),
                  yaxis=dict(title=ylabel if ylabel else y_col))
    if title is not None:
        layout['title'] = title
    if len(tbl_id) == 0:
        logger.debug('Using last_tblid: {}'.format(last_tblid))
        tbl_id = last_tblid
    marker_dict = dict(size=size, opacity=alpha)
    if color:
        marker_dict['color'] = color
    trace = dict(tbl_id=tbl_id, x='tables::' + x_col, y='tables::' + y_col,
                 mode='markers', type='scatter', marker=marker_dict)
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
    _confirm_fc()
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
    fc.show_chart(group_id=cell_id, layout=layout, data=[hist_data])
    return


def upload_table(table, title=None, show=True, write_func="auto", tbl_index=1, page_size=200,
                 view_coverage=False):
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
    _confirm_fc()
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
                    import warnings
                    from astropy.utils.exceptions import AstropyWarning
                    with warnings.catch_warnings():
                        warnings.simplefilter('ignore', AstropyWarning)
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
        tbl_id = gen_item_id('Table')
    else:
        tbl_id = title
    if view_coverage:
        coverage()
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
    cell_id: `str`
        cell id for the image. Defaults to the images cell default.

    Returns:
    --------
    image_id: `str`
        Image ID on the Firefly server
    """
    _confirm_fc()
    if isinstance(image, str):
        fval = fc.upload_file(image)
    else:
        if write_func == 'auto':
            if 'lsst.afw.image' in str(type(image)):
                write_func = image.writeFits
            elif 'astropy.io.fits' in str(type(image)):
                def write_astropy_image(fname):
                    import warnings
                    from astropy.utils.exceptions import AstropyWarning
                    with warnings.catch_warnings():
                        warnings.simplefilter('ignore', AstropyWarning)
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
        image_id = gen_item_id('Image')
        title = image_id
    else:
        image_id = title
    status = fc.show_fits(fval, plot_id=image_id, title=title, viewer_id=cell_id)
    if status['success']:
        global last_imageid
        last_imageid = image_id
        return image_id
    else:
        raise RuntimeError('image upload and display unsuccessful')


def coverage(cell_id=images_cellid):
    """Show a coverage image for the current table

    Parameters:
    -----------
    cell_id: `str`
        cell id for the image. Defaults to the images cell default.
    """
    _confirm_fc()
    fc.show_coverage(viewer_id=cell_id)
