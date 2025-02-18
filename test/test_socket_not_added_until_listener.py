import time

from firefly_client import FireflyClient
from pytest_container.container import Container, ContainerData, EntrypointSelection
from pytest_container.inspect import NetworkProtocol, PortForwarding


FIREFLY_CONTAINER = Container(
    url="docker.io/irsa/firefly:latest",
    extra_launch_args=["--memory=4g"],
    singleton=True,
    entry_point=EntrypointSelection.AUTO,
    forwarded_ports=[
        PortForwarding(
            container_port=8080,
            protocol=NetworkProtocol.TCP,
            host_port=8080,
            bind_ip="127.0.0.1",
        )
    ],
)

CONTAINER_IMAGES = [FIREFLY_CONTAINER]


def test_socket_not_added_until_listener(auto_container: ContainerData):
    assert auto_container.forwarded_ports[0].host_port == 8080
    host = f"http://{auto_container.forwarded_ports[0].bind_ip}:{auto_container.forwarded_ports[0].host_port}/firefly"

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
