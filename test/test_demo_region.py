import time
from test.container import FIREFLY_CONTAINER

import pytest
from astropy.utils.data import download_file
from pytest_container.container import ContainerData

from firefly_client import FireflyClient


@pytest.mark.parametrize("container", [FIREFLY_CONTAINER], indirect=["container"])
def test_region(container: ContainerData):
    assert container.forwarded_ports[0].host_port >= 8000
    assert container.forwarded_ports[0].host_port <= 65534
    assert container.forwarded_ports[0].container_port == 8080
    assert container.forwarded_ports[0].bind_ip == "127.0.0.1"

    time.sleep(5)

    host = f"http://{container.forwarded_ports[0].bind_ip}:{container.forwarded_ports[0].host_port}/firefly"

    fc = FireflyClient.make_client(url=host, launch_browser=False)

    # Download a sample image and table.
    #
    # We use astropy here for convenience, but firefly_client itself does not depend on astropy.

    # Download a cutout of a WISE band as 1 FITS image:
    image_url = (
        "http://irsa.ipac.caltech.edu/ibe/data/wise/allsky/4band_p1bm_frm/6a/02206a"
        + "/149/02206a149-w1-int-1b.fits?center=70,20&size=200pix"
    )
    filename = download_file(image_url, cache=True, timeout=120)

    # ## Display tables and catalogs

    # Instantiating FireflyClient should open a browser to the firefly server in a new tab. You can also achieve this using the following method. The browser open only works when running the notebook locally, otherwise a link is displayed.
    # localbrowser, browser_url = fc.launch_browser()

    # If it does not open automatically, try using the following command to display a web browser link to click on:
    fc.display_url()

    # Upload a local file to the server and then display it (while keeping in mind the `plot_id` parameter being chosen):
    imval = fc.upload_file(filename)
    status = fc.show_fits(
        file_on_server=imval, plot_id="region test", title="text region test"
    )

    # Add region data containing text region with 'textangle' property
    text_regions = [
        'image;text 100 150 # color=pink text={text angle is 30 deg } edit=0 highlite=0  font="Times 16 bold normal" textangle=30',
        'image;text 100 25 # color=pink text={text angle is -20 deg } font="Times 16 bold italic" textangle=-20',
        "circle  80.48446937 77.231180603 13.9268922 #  text={physical;circle ;; color=cyan } color=cyan",
        "image;box 100 150 60 30 30 # color=red text={box on # J2000 with size w=60 & h=30}",
        "circle  80.484469p 77.231180p 3.002392 # color=#B8E986 text={This message has both a \" and ' in it}",
    ]
    status = fc.add_region_data(
        region_data=text_regions,
        region_layer_id="layerTextRegion",
        plot_id="region test",
    )
    assert status is not None
