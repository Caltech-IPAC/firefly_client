import time

import pytest
from astropy.utils.data import download_file

from firefly_client import FireflyClient
from pytest_container.container import ContainerData

from pytest_mock import MockerFixture
from test.container import FIREFLY_CONTAINER


@pytest.mark.parametrize("container", [FIREFLY_CONTAINER], indirect=["container"])
def test_adv_steps(container: ContainerData, mocker: MockerFixture):
    assert container.forwarded_ports[0].host_port >= 8000
    assert container.forwarded_ports[0].host_port <= 65534
    assert container.forwarded_ports[0].container_port == 8080
    assert container.forwarded_ports[0].bind_ip == "127.0.0.1"

    mocker.patch("webbrowser.open")
    time.sleep(5)

    host = f"http://{container.forwarded_ports[0].bind_ip}:{container.forwarded_ports[0].host_port}/firefly"

    fc = FireflyClient.make_client(url=host, launch_browser=False)
    fc.change_triview_layout(FireflyClient.BIVIEW_T_IChCov)

    # ## Display tables, images, XY charts, and Histograms in Window/Grid like layout
    #
    # Each rendered unit on Firefly Slate Viewer is called a'cell'. To render a cell and its content, the cell location (row, column, width, height), element type and cell ID are needed. (row, column) and (width, height) represent the position and size of the cell in terms of the grid blocks on Firefly Slate Viewer. Element types include types of 'tables', images', 'xyPlots', 'tableImageMeta' and 'coverageImage'.

    # We use astropy here for convenience, but firefly_client itself does not depend on astropy.

    #
    # ## Display tables and catalogs
    #
    #
    # Add some tables into cell 'main' (default cell id for tables)
    #
    #
    # -  add first table in cell 'main':
    # -  'main' is the cell id currently supported by Firefly for element type 'tables'
    # -  this cell is shown at row = 0, col = 0 with width = 4, height = 2

    tbl_name = download_file(
        "http://web.ipac.caltech.edu/staff/roby/demo/moving/MOST_results-sample.tbl",
        timeout=120,
        cache=True,
    )
    meta_info = {
        "datasetInfoConverterId": "SimpleMoving",
        "positionCoordColumns": "ra_obj;dec_obj;EQ_J2000",
        "datasource": "image_url",
    }
    fc.show_table(
        fc.upload_file(tbl_name),
        tbl_id="movingtbl",
        title="A moving object table",
        page_size=15,
        meta=meta_info,
    )

    # -  add 2nd table in cell 'main' for chart and histogram
    tbl_name = download_file(
        "http://web.ipac.caltech.edu/staff/roby/demo/WiseDemoTable.tbl",
        timeout=120,
        cache=True,
    )
    fc.show_table(
        fc.upload_file(tbl_name),
        tbl_id="tbl_chart",
        title="table for xyplot and histogram",
        page_size=15,
    )

    # -  add 3rd table in cell 'main'
    tbl_name = download_file(
        "http://web.ipac.caltech.edu.s3-us-west-2.amazonaws.com/staff/roby/data-products-test/dp-test.tbl",
        timeout=120,
        cache=True,
    )
    meta_info = {"datasource": "DP"}
    fc.show_table(
        fc.upload_file(tbl_name),
        title="A table of simple images",
        page_size=15,
        meta=meta_info,
    )

    # -  add 4th table in cell 'main'
    tbl_name = download_file(
        "http://web.ipac.caltech.edu/staff/roby/demo/test-table-m31.tbl",
        timeout=120,
        cache=True,
    )

    meta_info = {
        "positionCoordColumns": "ra_obj;dec_obj;EQ_J2000",
        "datasource": "FITS",
    }
    fc.show_table(
        fc.upload_file(tbl_name),
        title="A table of m31 images",
        page_size=15,
        meta=meta_info,
    )

    # ## Add different types of image displays
    #
    # -  show cell with id 'image-meta' containaing image from the active table containing datasource column in cell 'main'
    # -  the cell is shown at row = 2, col = 0 with width = 4, height = 2
    # -  show cell 'wise-content' containing fits at row = 0, col = 4 with width = 2, height = 2
    image_name = download_file(
        "http://irsa.ipac.caltech.edu/ibe/data/wise/allsky/4band_p1bm_frm/6a/02206a"
        + "/149/02206a149-w1-int-1b.fits?center=70,20&size=200pix"
    )
    fc.show_fits(file_on_server=fc.upload_file(image_name), title="WISE Cutout")

    # -  show 4 fits of moving objects in cell 'movingStff' at row = 2, col = 4 with width = 2, height = 2
    fc.show_fits(
        plot_id="m49025b_143_2",
        OverlayPosition="330.347003;-2.774482;EQ_J2000",
        ZoomType="TO_WIDTH_HEIGHT",
        Title="49025b143-w2",
        plotGroupId="movingGroup",
        URL="http://web.ipac.caltech.edu/staff/roby/demo/moving/49025b143-w2-int-1b.fits",
    )
    fc.show_fits(
        plot_id="m49273b_134_2",
        OverlayPosition="333.539702;-0.779310;EQ_J2000",
        ZoomType="TO_WIDTH_HEIGHT",
        Title="49273b134-w2",
        plotGroupId="movingGroup",
        URL="http://web.ipac.caltech.edu/staff/roby/demo/moving/49273b134-w2-int-1b.fits",
    )
    fc.show_fits(
        plot_id="m49277b_135_1",
        OverlayPosition="333.589054;-0.747251;EQ_J2000",
        ZoomType="TO_WIDTH_HEIGHT",
        Title="49277b135-w1",
        plotGroupId="movingGroup",
        URL="http://web.ipac.caltech.edu/staff/roby/demo/moving/49277b135-w1-int-1b.fits",
    )
    fc.show_fits(
        plot_id="m49289b_134_2",
        OverlayPosition="333.736578;-0.651222;EQ_J2000",
        ZoomType="TO_WIDTH_HEIGHT",
        Title="49289b134-w2",
        plotGroupId="movingGroup",
        URL="http://web.ipac.caltech.edu/staff/roby/demo/moving/49289b134-w2-int-1b.fits",
    )

    # ## Add charts (xy plot and histogram)
    #
    # -  show the cell 'chart-cell-xy' with xy plot related to the table with id 'tbl_chart' in cell 'main'
    # -  this cell is shown at row = 4, col = 0 with width = 2, height = 3
    trace1 = {
        "tbl_id": "tbl_chart",
        "x": "tables::ra1",
        "y": "tables::dec1",
        "mode": "markers",
        "type": "scatter",
        "marker": {"size": 4},
    }
    trace_data = [trace1]

    layout_s = {
        "title": "Coordinates",
        "xaxis": {"title": "ra1 (deg)"},
        "yaxis": {"title": "dec1 (deg)"},
    }
    fc.show_chart(layout=layout_s, data=trace_data)

    # -  show the cell with histogram related to the table with id 'tbl_chart' in cell 'main',
    # -  this cell is shown at row = 4, col = 2, with width = 2, height = 3
    # -  the cell id is automatically created by FireflyClient in case it is not specified externally.
    histData = [
        {
            "type": "fireflyHistogram",
            "name": "magzp",
            "marker": {"color": "rgba(153, 51, 153, 0.8)"},
            "firefly": {
                "tbl_id": "tbl_chart",
                "options": {
                    "algorithm": "fixedSizeBins",
                    "fixedBinSizeSelection": "numBins",
                    "numBins": 30,
                    "columnOrExpr": "magzp",
                },
            },
        }
    ]

    layout_hist = {
        "title": "Magnitude Zeropoints",
        "xaxis": {"title": "magzp"},
        "yaxis": {"title": ""},
    }
    result = fc.show_chart(layout=layout_hist, data=histData)
    assert result is not None

    # ## Add more images
    #
    # -  show coverage image associated with the active table in cell 'main'
    # -  this cell is shown at row = 4, col = 4 with width = 2, height = 3
    # -  show image in random location without passing cell location and cell id (i.e. without calling add_cell)
    # -  the image is shown in the cell with id 'DEFAULT_FITS_VIEWER_ID' in default,
    # -  and the cell is automatically located by Firefly
    img_name = download_file(
        "http://web.ipac.caltech.edu/staff/roby/demo/wise-m51-band2.fits",
        timeout=120,
        cache=True,
    )
    fc.show_fits(file_on_server=fc.upload_file(img_name))
    fc.show_fits(plot_id="zzz", file_on_server=fc.upload_file(img_name))

    # -  show second image in random. it is shown in the same cell as the previous one
    fc.show_fits(
        plot_id="xxq",
        Service="TWOMASS",
        Title="2mass from service",
        ZoomType="LEVEL",
        initZoomLevel=2,
        SurveyKey="asky",
        SurveyKeyBand="k",
        WorldPt="10.68479;41.26906;EQ_J2000",
        SizeInDeg=".12",
    )
