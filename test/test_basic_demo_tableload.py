import os
import time
from pathlib import Path
from urllib import request

import pytest
from firefly_client import FireflyClient
from pytest_container.container import ContainerData
from pytest_mock import MockerFixture
from test.container import FIREFLY_CONTAINER


@pytest.mark.parametrize("container", [FIREFLY_CONTAINER], indirect=["container"])
def test_basic_tableload(container: ContainerData, mocker: MockerFixture):
    assert container.forwarded_ports[0].host_port >= 8000
    assert container.forwarded_ports[0].host_port <= 65534
    assert container.forwarded_ports[0].container_port == 8080
    assert container.forwarded_ports[0].bind_ip == "127.0.0.1"
    mocker.patch("webbrowser.open")
    time.sleep(5)

    host = f"http://{container.forwarded_ports[0].bind_ip}:{container.forwarded_ports[0].host_port}/firefly"

    fc = FireflyClient.make_client(url=host, launch_browser=False)

    test_data_path = Path(os.curdir)

    # This was originally /hydra/cm/MF.20210502.18830.fits
    localfile = os.path.join(test_data_path, "wise-00.fits")

    request.urlretrieve(
        "http://web.ipac.caltech.edu.s3-us-west-2.amazonaws.com/staff/roby/demo/wise-00.fits",
        localfile,
    )

    filename = fc.upload_file(localfile)
    fc.show_table(filename)
    fc.show_table(filename, table_index=2)

    # localfile = os.path.join(testdata_repo_path, "Mr31objsearch.xml")
    # filename = fc.upload_file(localfile)

    # fc.show_table(filename, tbl_id="votable-0")
    # fc.show_table(filename, tbl_id="votable-1", table_index=1)

    os.remove(localfile)
