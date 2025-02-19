import random

from pytest_container.container import Container, EntrypointSelection
from pytest_container.inspect import NetworkProtocol, PortForwarding

FIREFLY_CONTAINER = Container(
    url="docker.io/ipac/firefly:latest",
    extra_launch_args=["--memory=4g"],
    entry_point=EntrypointSelection.AUTO,
    singleton=True,
    forwarded_ports=[
        PortForwarding(
            container_port=8080,
            protocol=NetworkProtocol.TCP,
            host_port=random.randint(8000, 65534),
            bind_ip="127.0.0.1",
        )
    ],
)
