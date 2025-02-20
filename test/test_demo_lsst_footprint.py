import time
from test.container import FIREFLY_CONTAINER

import pytest
from astropy.utils.data import download_file
from pytest_container.container import ContainerData

from firefly_client import FireflyClient


@pytest.mark.parametrize("container", [FIREFLY_CONTAINER], indirect=["container"])
def test_lsst_footprint(container: ContainerData):
    assert container.forwarded_ports[0].host_port >= 8000
    assert container.forwarded_ports[0].host_port <= 65534
    assert container.forwarded_ports[0].container_port == 8080
    assert container.forwarded_ports[0].bind_ip == "127.0.0.1"

    time.sleep(5)

    host = f"http://{container.forwarded_ports[0].bind_ip}:{container.forwarded_ports[0].host_port}/firefly"

    fc = FireflyClient.make_client(
        url=host, launch_browser=False
    )  # ## Start with Image Data

    # The data used in this example are taken from http://web.ipac.caltech.edu/staff/shupe/firefly_testdata and can be downloaded. Download a file using the image URL below and upload it to the server:
    image_url = "http://web.ipac.caltech.edu/staff/shupe/firefly_testdata/calexp-subset-HSC-R.fits"
    filename = download_file(image_url, cache=True, timeout=120)
    imval = fc.upload_file(filename)

    # Set the `plot_id` for the image and display it through the opened browser:
    plotid = "footprinttest"
    status = fc.show_fits(
        file_on_server=imval, plot_id=plotid, title="footprints HSC R-band"
    )

    # ## Add Data for Footprints

    # Upload a table with footprint data using the following url from where it can be downloaded:
    table_url = "http://web.ipac.caltech.edu/staff/shupe/firefly_testdata/footprints-subset-HSC-R.xml"
    footprint_table = download_file(table_url, cache=True, timeout=120)
    tableval = fc.upload_file(footprint_table)

    # Overlay a footprint layer (while comparing a highlighted section to the overall footprint) onto the plot using the above table:
    status = fc.overlay_footprints(
        tableval,
        title="footprints HSC R-band",
        footprint_layer_id="footprint_layer_1",
        plot_id=plotid,
        highlightColor="yellow",
        selectColor="cyan",
        style="fill",
        color="rgba(74,144,226,0.30)",
    )
    assert status is not None
