import astropy.utils.data


def download_from(url):
    return astropy.utils.data.download_file(url, timeout=120, cache=True)


def load_moving_table(row, col, width, height, fc, cell_id=None):
    moving_tbl_name = download_from("http://web.ipac.caltech.edu/staff/roby/demo/moving/MOST_results-sample.tbl")

    r = fc.add_cell(row, col, width, height, 'tables', cell_id)
    meta_info = {'datasetInfoConverterId': 'SimpleMoving',
                 'positionCoordColumns': 'ra_obj;dec_obj;EQ_J2000',
                 'datasource': 'image_url'}
    tbl_name = fc.upload_file(moving_tbl_name)

    if r['success']:
        fc.show_table(tbl_name, tbl_id='movingtbl', title='A moving object table',
                      page_size=15, meta=meta_info)


def add_simple_m31_image_table(fc):
    tbl_name = download_from("http://web.ipac.caltech.edu/staff/roby/demo/test-table-m31.tbl")

    meta_info = {'positionCoordColumns': 'ra_obj;dec_obj;EQ_J2000',
                 'datasource': 'FITS'}
    fc.show_table(fc.upload_file(tbl_name), title='A table of m31 images', page_size=15, meta=meta_info)


def add_simple_image_table(fc):
    tbl_name = download_from("http://web.ipac.caltech.edu/staff/roby/demo/test-table4.tbl")

    meta_info = {'datasource': 'FITS'}
    fc.show_table(fc.upload_file(tbl_name), title='A table of simple images', page_size=15, meta=meta_info)


def add_table_for_chart(fc):
    tbl_name = download_from('http://web.ipac.caltech.edu/staff/roby/demo/WiseDemoTable.tbl')

    fc.show_table(fc.upload_file(tbl_name), tbl_id='tbl_chart', title='table for xyplot and histogram', page_size=15)


def load_image(row, col, width, height, fc, cell_id=None):
    r = fc.add_cell(row, col, width, height, 'images', cell_id)

    image_name = download_from('http://irsa.ipac.caltech.edu/ibe/data/wise/allsky/4band_p1bm_frm/6a/02206a' +
                               '/149/02206a149-w1-int-1b.fits?center=70,20&size=200pix')

    if r['success']:
        fc.show_fits(file_on_server=fc.upload_file(image_name), viewer_id=r['cell_id'], title='WISE Cutout')


def load_image_metadata(row, col, width, height, fc, cell_id=None):
    r = fc.add_cell(row, col, width, height, 'tableImageMeta', cell_id)

    if r['success']:
        fc.show_image_metadata(viewer_id=r['cell_id'])


def load_coverage_image(row, col, width, height, fc, cell_id=None):
    r = fc.add_cell(row, col, width, height, 'coverageImage', cell_id)

    if r['success']:
        fc.show_coverage(viewer_id=r['cell_id'])


def load_moving(row, col, width, height, fc, cell_id=None):
    r = fc.add_cell(row, col, width, height, 'images', cell_id)

    if r['success']:
        v_id = r['cell_id']
        fc.show_fits(plot_id='m49025b_143_2', viewer_id=v_id,  OverlayPosition='330.347003;-2.774482;EQ_J2000',
                     ZoomType='TO_WIDTH_HEIGHT', Title='49025b143-w2', plotGroupId='movingGroup',
                     URL='http://web.ipac.caltech.edu/staff/roby/demo/moving/49025b143-w2-int-1b.fits')
        fc.show_fits(plot_id='m49273b_134_2', viewer_id=v_id,  OverlayPosition='333.539702;-0.779310;EQ_J2000',
                     ZoomType='TO_WIDTH_HEIGHT', Title='49273b134-w2', plotGroupId='movingGroup',
                     URL='http://web.ipac.caltech.edu/staff/roby/demo/moving/49273b134-w2-int-1b.fits')
        fc.show_fits(plot_id='m49277b_135_1', viewer_id=v_id,  OverlayPosition='333.589054;-0.747251;EQ_J2000',
                     ZoomType='TO_WIDTH_HEIGHT', Title='49277b135-w1', plotGroupId='movingGroup',
                     URL='http://web.ipac.caltech.edu/staff/roby/demo/moving/49277b135-w1-int-1b.fits')
        fc.show_fits(plot_id='m49289b_134_2', viewer_id=v_id,  OverlayPosition='333.736578;-0.651222;EQ_J2000',
                     ZoomType='TO_WIDTH_HEIGHT', Title='49289b134-w2', plotGroupId='movingGroup',
                     URL='http://web.ipac.caltech.edu/staff/roby/demo/moving/49289b134-w2-int-1b.fits')


def load_xy(row, col, width, height, fc, cell_id=None):
    r = fc.add_cell(row, col, width, height, 'xyPlots', cell_id)

    if r['success']:
        fc.show_xyplot('tbl_chart', group_id=r['cell_id'], xCol='ra1', yCol='dec1')


def load_histogram(row, col, width, height, fc, cell_id=None):
    r = fc.add_cell(row, col, width, height, 'xyPlots', cell_id)

    if r['success']:
        fc.show_histogram('tbl_chart', group_id=r['cell_id'], col='modeint', xOptions='log')


def load_first_image_in_random(fc):
    img_name = download_from('http://web.ipac.caltech.edu/staff/roby/demo/wise-m51-band2.fits')

    fc.show_fits(file_on_server=fc.upload_file(img_name))


def load_second_image_in_random(fc):
    fc.show_fits(plot_id='xxq', Service='TWOMASS', Title='2mass from service', ZoomType='LEVEL',
                 initZoomLevel=2, SurveyKey='k', WorldPt='10.68479;41.26906;EQ_J2000',
                 RangeValues='92,-1,92,2,1,0,1,2,44,120', SizeInDeg='.12')

