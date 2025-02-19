import os
import random
import time

from firefly_client import FireflyClient
from pytest_container.container import Container, ContainerData, EntrypointSelection
from pytest_container.inspect import NetworkProtocol, PortForwarding

FIREFLY_CONTAINER = Container(
    url="docker.io/ipac/firefly:latest",
    extra_launch_args=["--memory=4g"],
    entry_point=EntrypointSelection.AUTO,
    forwarded_ports=[
        PortForwarding(
            container_port=8080,
            protocol=NetworkProtocol.TCP,
            host_port=random.randint(8000, 65534),
            bind_ip="127.0.0.1",
        )
    ],
)

CONTAINER_IMAGES = [FIREFLY_CONTAINER]


def test_tableload(auto_container: ContainerData):
    assert auto_container.forwarded_ports[0].host_port >= 8000
    assert auto_container.forwarded_ports[0].host_port <= 65534
    assert auto_container.forwarded_ports[0].container_port == 8080
    assert auto_container.forwarded_ports[0].bind_ip == "127.0.0.1"

    time.sleep(5)
    host = f"http://{auto_container.forwarded_ports[0].bind_ip}:{auto_container.forwarded_ports[0].host_port}/firefly"
    fc = FireflyClient.make_client(host)

    testdata_repo_path = "/hydra/cm"

    localfile = os.path.join(testdata_repo_path, "MF.20210502.18830.fits")
    filename = fc.upload_file(localfile)

    fc.show_table(filename)

    fc.show_table(filename, table_index=2)

    localfile = os.path.join(testdata_repo_path, "Mr31objsearch.xml")
    filename = fc.upload_file(localfile)

    fc.show_table(filename, tbl_id="votable-0")

    fc.show_table(filename, tbl_id="votable-1", table_index=1)
