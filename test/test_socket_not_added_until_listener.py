import time

import pytest

from firefly_client import FireflyClient
from pytest_container.container import ContainerData

from pytest_mock import MockerFixture
from test.container import FIREFLY_CONTAINER


@pytest.mark.parametrize("container", [FIREFLY_CONTAINER], indirect=["container"])
def test_socket_not_added_until_listener(
    container: ContainerData, mocker: MockerFixture
):
    assert container.forwarded_ports[0].host_port >= 8000
    assert container.forwarded_ports[0].host_port <= 65534
    assert container.forwarded_ports[0].container_port == 8080
    assert container.forwarded_ports[0].bind_ip == "127.0.0.1"
    mocker.patch("webbrowser.open")
    time.sleep(5)

    host = f"http://{container.forwarded_ports[0].bind_ip}:{container.forwarded_ports[0].host_port}/firefly"

    channel1 = "channel-test-1"

    fc1_c1 = FireflyClient.make_client(
        host, channel_override=channel1, launch_browser=False
    )
    fc1_c1.show_fits(
        url="http://web.ipac.caltech.edu.s3-us-west-2.amazonaws.com/staff/roby/demo/wise-00.fits"
    )

    fc1_c1.add_extension(ext_type="LINE_SELECT", title="a line")
    fc1_c1.add_extension(ext_type="AREA_SELECT", title="a area")
    fc1_c1.add_extension(ext_type="POINT", title="a point")

    def listener1(ev):
        print("l1")
        print(ev)

    fc1_c1.add_listener(listener1)
    time.sleep(1)
    fc1_c1.remove_listener(listener1)
    time.sleep(1)
    fc1_c1.disconnect()
