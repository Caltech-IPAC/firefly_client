import time

from pytest_mock import MockerFixture
from test.container import FIREFLY_CONTAINER

import pytest
from astropy.io import fits
from astropy.table import Table
from astropy.utils.data import download_file
from pytest_container.container import ContainerData

from firefly_client import FireflyClient
from firefly_client import plot as ffplt


@pytest.mark.parametrize("container", [FIREFLY_CONTAINER], indirect=["container"])
def test_plt(container: ContainerData, mocker: MockerFixture):
    assert container.forwarded_ports[0].host_port >= 8000
    assert container.forwarded_ports[0].host_port <= 65534
    assert container.forwarded_ports[0].container_port == 8080
    assert container.forwarded_ports[0].bind_ip == "127.0.0.1"
    mocker.patch("webbrowser.open")
    time.sleep(5)

    host = f"http://{container.forwarded_ports[0].bind_ip}:{container.forwarded_ports[0].host_port}/firefly"

    fc = FireflyClient.make_client(url=host, launch_browser=False)

    ffplt.use_client(fc)

    # The next cell will attempt to launch a browser, if there is not already a web page connected to the instance of `FireflyClient`.
    ffplt.open_browser()

    # If the browser launch is unsuccessful, a link will be displayed for your web browser.

    # The next cell will display a clickable link
    ffplt.display_url()

    # #### Optional: specifying a server and channel.
    #
    # By default, a channel is generated for you. If you find it more convenient to use a specific server and channel, uncomment out the next cell to generate a channel from your username.
    # ## Restart here

    # If needed, clear the viewer and reset the layout to the defaults.
    ffplt.clear()
    ffplt.reset_layout()

    # ### Upload a table directly from disk.
    # For the case of a file already on disk, pass the path and a title for the table. Here we download a file.
    m31_table_fname = download_file(
        "http://web.ipac.caltech.edu/staff/roby/demo/m31-2mass-2412-row.tbl",
        timeout=120,
        cache=True,
    )

    # Upload the table file from disk, and enable the coverage image
    tbl_id = ffplt.upload_table(m31_table_fname, title="M31 2MASS", view_coverage=True)
    assert tbl_id is not None

    # Make a histogram from the last uploaded table, with the minimum required parameters
    ffplt.hist("j_m")

    # Make a scatter plot from the last uploaded table, with the minimum required parameters
    ffplt.scatter("h_m - k_m", "j_m")

    # ### Viewing a Python image object

    # Load a FITS file using astropy.io.fits

    m31_image_fname = download_file(
        "http://web.ipac.caltech.edu/staff/roby/demo/2mass-m31-green.fits",
        timeout=120,
        cache=True,
    )
    hdu = fits.open(m31_image_fname)
    type(hdu)

    # Upload to the viewer. The return value is the `plot_id`.

    # In[13]:

    ffplt.upload_image(hdu)

    # ### Viewing a Numpy array

    # If the `astropy` package is installed, a Numpy array can be uploaded.

    # In[14]:

    data = hdu[0].data
    type(data)

    # Upload to the viewer. The return value is the `plot_id`.

    # In[15]:

    ffplt.upload_image(data)

    # ### Uploading a Python table object

    # Load a table using astropy

    # In[16]:

    wise_tbl_name = download_file(
        "http://web.ipac.caltech.edu/staff/roby/demo/WiseDemoTable.tbl",
        timeout=120,
        cache=True,
    )

    # Read the downloaded table in IPAC table format

    wise_table = Table.read(wise_tbl_name, format="ipac")

    # Upload to the viewer with a set title

    ffplt.upload_table(wise_table, title="WISE Demo Table")
