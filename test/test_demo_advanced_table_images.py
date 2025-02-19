import time

import pytest
from firefly_client import FireflyClient
from pytest_container.container import ContainerData
from test import firefly_slate_demo as fs
from test.container import FIREFLY_CONTAINER


@pytest.mark.parametrize("container", [FIREFLY_CONTAINER])
def test_adv_table_imgs(container: ContainerData):
    assert container.forwarded_ports[0].host_port >= 8000
    assert container.forwarded_ports[0].host_port <= 65534
    assert container.forwarded_ports[0].container_port == 8080
    assert container.forwarded_ports[0].bind_ip == "127.0.0.1"

    time.sleep(5)

    host = f"http://{container.forwarded_ports[0].bind_ip}:{container.forwarded_ports[0].host_port}/firefly"

    fc = FireflyClient.make_client(url=host, launch_browser=False)

    # ## Display tables and catalogs

    # Instantiating FireflyClient should open a browser to the firefly server in a new tab. You can also achieve this using the following method. The browser open only works when running the notebook locally, otherwise a link is displayed.
    # Add some tables into cell 'main' (default grid viewer id for tables)
    # first table in cell 'main'
    fs.load_moving_table(0, 0, 4, 2, fc)

    # add table in cell 'main' for chart and histogram
    fs.add_table_for_chart(fc)
    # add table in cell 'main'
    fs.add_simple_image_table(fc)
    # add table in cell 'main'
    fs.add_simple_m31_image_table(fc)
    # ## Add different types of image displays
    # show cell containing the image from the active table with datasource column in cell 'main'
    fs.load_image_metadata(2, 0, 4, 2, fc, "image-meta")
    # show cell containing FITS in cell 'wise-cutout'
    fs.load_image(0, 4, 2, 2, fc, "wise-cutout")  # load an image
    # show cell with 4 FITS of moving objects in cell 'movingStff'
    fs.load_moving(2, 4, 2, 2, fc, "movingStuff")
    # ## Add charts (xy plot and histogram)
    # show xy plot in cell 'chart-cell-xy' associated with the table for chart in cell 'main'
    fs.load_xy(4, 0, 2, 3, fc, "chart-cell-xy")
    # show histogram associated with the table for chart in cell 'main', the cell id is generated by firefly_client
    fs.load_histogram(4, 2, 2, 3, fc)
    # ## Add more images
    # show cell containing coverage image associated with the active table in cell 'main'
    fs.load_coverage_image(4, 4, 3, 3, fc, "image-coverage")
    # show cell containing image in ranmon location without passing the location and cell id
    fs.load_first_image_in_random(fc)
    # show second image in random location. This image is located in the same cell as the previous one
    fs.load_second_image_in_random(fc)
