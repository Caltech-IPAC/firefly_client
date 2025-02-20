import time
from test.container import FIREFLY_CONTAINER

import pytest
from pytest_container.container import ContainerData

from firefly_client import FireflyClient


@pytest.mark.parametrize("container", [FIREFLY_CONTAINER], indirect=["container"])
def test_hi_ps(container: ContainerData):
    assert container.forwarded_ports[0].host_port >= 8000
    assert container.forwarded_ports[0].host_port <= 65534
    assert container.forwarded_ports[0].container_port == 8080
    assert container.forwarded_ports[0].bind_ip == "127.0.0.1"

    time.sleep(5)

    host = f"http://{container.forwarded_ports[0].bind_ip}:{container.forwarded_ports[0].host_port}/firefly"

    fc = FireflyClient.make_client(url=host, launch_browser=False)

    target = "148.892;69.0654;EQ_J2000"

    viewer_id = "hipsDIV1"
    r = fc.add_cell(0, 0, 4, 2, "images", viewer_id)
    if r["success"]:
        hips_url = "http://alasky.u-strasbg.fr/DSS/DSSColor"
        status = fc.show_hips(
            viewer_id=viewer_id,
            plot_id="aHipsID1-1",
            hips_root_url=hips_url,
            Title="HiPS-DSS",
            WorldPt=target,
        )

    fc.set_color("aHipsID1-1", colormap_id=6, bias=0.6, contrast=1.5)

    hips_url = "http://alasky.u-strasbg.fr/DSS/DSS2Merged"
    status = fc.show_hips(
        plot_id="aHipsID1-2", hips_root_url=hips_url, Title="HiPS-DSS2", WorldPt=target
    )

    assert status is not None

    hips_url = "http://alasky.u-strasbg.fr/AllWISE/RGB-W4-W2-W1"
    status = fc.show_hips(plot_id="aHipsID2", hips_root_url=hips_url)

    assert status is not None
