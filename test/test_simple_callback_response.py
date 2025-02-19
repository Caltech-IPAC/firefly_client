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


def test_simple_callback_response(auto_container: ContainerData):
    assert auto_container.forwarded_ports[0].host_port >= 8000
    assert auto_container.forwarded_ports[0].host_port <= 65534
    assert auto_container.forwarded_ports[0].container_port == 8080
    assert auto_container.forwarded_ports[0].bind_ip == "127.0.0.1"

    time.sleep(5)

    FireflyClient._debug = False
    token = None
    host = f"http://{auto_container.forwarded_ports[0].bind_ip}:{auto_container.forwarded_ports[0].host_port}/firefly"
    # fc = FireflyClient.make_client(host, channel_override=channel1, launch_browser=True, token=token)
    fc = FireflyClient.make_client(host, launch_browser=False, token=token)
    print(fc.get_firefly_url())
    fc.show_fits(
        url="http://web.ipac.caltech.edu.s3-us-west-2.amazonaws.com/staff/roby/demo/wise-00.fits"
    )

    def example_listener(ev):
        if False:
            print(ev)
        if "data" not in ev:
            print("no data found in ev")
            return
        data = ev["data"]
        if "payload" in data:
            print(data["payload"])
        if "type" in data:
            print(data["type"])
            if data["type"] == "POINT":
                print("   plotId: " + data["plotId"])
                print("   image point: %s" % data["ipt"])
                print("   world point: %s" % data["wpt"])
            if data["type"] == "LINE_SELECT" or data["type"] == "AREA_SELECT":
                print("   plotId: " + data["plotId"])
                print("   image points: %s to %s" % (data["ipt0"], data["ipt1"]))
                print("   world points: %s to %s" % (data["wpt0"], data["wpt1"]))

    fc.add_extension(
        ext_type="POINT", title="Output Selected Point", shortcut_key="ctrl-p"
    )
    fc.add_extension(
        ext_type="LINE_SELECT", title="Output Selected line", shortcut_key="meta-b"
    )
    fc.add_extension(
        ext_type="AREA_SELECT", title="Output Selected Area", shortcut_key="a"
    )
    # ------------ add listener and wait
    fc.add_listener(example_listener)
    print("listener is added")
    # time.sleep(3)
    # fc.remove_listener(example_listener)
    # time.sleep(2)
    # fc.add_listener(example_listener)
