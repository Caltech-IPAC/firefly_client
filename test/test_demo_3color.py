import time

import pytest
from pytest_mock import MockerFixture
from pytest_container.container import ContainerData

from test.container import FIREFLY_CONTAINER

from firefly_client import FireflyClient


@pytest.mark.parametrize("container", [FIREFLY_CONTAINER], indirect=["container"])
def test_3color(container: ContainerData, mocker: MockerFixture):
    assert container.forwarded_ports[0].host_port >= 8000
    assert container.forwarded_ports[0].host_port <= 65534
    assert container.forwarded_ports[0].container_port == 8080
    assert container.forwarded_ports[0].bind_ip == "127.0.0.1"
    mocker.patch("webbrowser.open")
    time.sleep(5)

    host = f"http://{container.forwarded_ports[0].bind_ip}:{container.forwarded_ports[0].host_port}/firefly"

    fc = FireflyClient.make_client(url=host, launch_browser=False)

    target = "210.80227;54.34895;EQ_J2000"  # Galaxy M101
    viewer_id = "3C"
    r = fc.add_cell(0, 0, 1, 1, "images", viewer_id)
    rv = "92,-2,92,8,NaN,2,44,25,600,120"
    if r["success"]:
        threeC = [
            {
                "Type": "SERVICE",
                "Service": "WISE",
                "Title": "3 color",
                "SurveyKey": "3a",
                "SurveyKeyBand": "3",
                "WorldPt": target,
                "RangeValues": rv,
                "SizeInDeg": ".14",
            },
            {
                "Type": "SERVICE",
                "Service": "WISE",
                "Title": "3 color",
                "SurveyKey": "3a",
                "SurveyKeyBand": "2",
                "WorldPt": target,
                "RangeValues": rv,
                "SizeInDeg": ".14",
            },
            {
                "Type": "SERVICE",
                "Service": "WISE",
                "Title": "3 color",
                "SurveyKey": "3a",
                "SurveyKeyBand": "1",
                "WorldPt": target,
                "RangeValues": rv,
                "SizeInDeg": ".14",
            },
        ]

        fc.show_fits_3color(threeC, plot_id="wise_m101", viewer_id=viewer_id)
    # Set stretch using hue-preserving algorithm with scaling coefficients .15 for RED, 1.0 for GREEN, and .4 for BLUE.
    fc.set_stretch_hprgb(
        plot_id="wise_m101", asinh_q_value=4.2, scaling_k=[0.15, 1, 0.4]
    )
    # Set per-band stretch
    fc.set_stretch(plot_id="wise_m101", stype="ztype", algorithm="asinh", band="ALL")
    # Set contrast and bias for each band
    fc.set_rgb_colors(plot_id="wise_m101", bias=[0.4, 0.6, 0.5], contrast=[1.5, 1, 2])
    # Set to use red and blue band only, with default bias and contrast
    fc.set_rgb_colors(plot_id="wise_m101", use_green=False)
