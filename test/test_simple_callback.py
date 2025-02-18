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


def test_simple_callback(auto_container: ContainerData):
    assert auto_container.forwarded_ports[0].host_port == 8080
    host = f"http://{auto_container.forwarded_ports[0].bind_ip}:{auto_container.forwarded_ports[0].host_port}/firefly"
    channel1 = "channel-test-1"
    FireflyClient._debug = False
    fc = FireflyClient.make_client(
        host, channel_override=channel1, launch_browser=False
    )
    # fc = FireflyClient.make_lab_client(start_tab=False)
    firefly_url = fc.get_firefly_url()
    assert host in firefly_url
