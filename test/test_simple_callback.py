import time

import pytest
from pytest_mock import MockerFixture
from pytest_container.container import ContainerData

from test.container import FIREFLY_CONTAINER

from firefly_client import FireflyClient


@pytest.mark.parametrize("container", [FIREFLY_CONTAINER], indirect=["container"])
def test_simple_callback(container: ContainerData, mocker: MockerFixture):
    assert container.forwarded_ports[0].host_port >= 8000
    assert container.forwarded_ports[0].host_port <= 65534
    assert container.forwarded_ports[0].container_port == 8080
    assert container.forwarded_ports[0].bind_ip == "127.0.0.1"
    mocker.patch("webbrowser.open")
    time.sleep(5)

    host = f"http://{container.forwarded_ports[0].bind_ip}:{container.forwarded_ports[0].host_port}/firefly"
    channel1 = "channel-test-1"
    FireflyClient._debug = False
    fc = FireflyClient.make_client(
        host, channel_override=channel1, launch_browser=False
    )
    # fc = FireflyClient.make_lab_client(start_tab=False)
    firefly_url = fc.get_firefly_url()
    assert host in firefly_url
