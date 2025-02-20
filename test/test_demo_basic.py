import time
from test.container import FIREFLY_CONTAINER

import pytest
from astropy.utils.data import download_file
from pytest_container.container import ContainerData

from firefly_client import FireflyClient


@pytest.mark.parametrize("container", [FIREFLY_CONTAINER], indirect=["container"])
def test_basics(container: ContainerData):
    assert container.forwarded_ports[0].host_port >= 8000
    assert container.forwarded_ports[0].host_port <= 65534
    assert container.forwarded_ports[0].container_port == 8080
    assert container.forwarded_ports[0].bind_ip == "127.0.0.1"

    time.sleep(5)

    host = f"http://{container.forwarded_ports[0].bind_ip}:{container.forwarded_ports[0].host_port}/firefly"

    fc = FireflyClient.make_client(url=host, launch_browser=False)
    # ## Download Sample Data
    # For the following example, we download a sample image and table by using astropy (it's used only for convenience, firefly_client itself does not depend on astropy):
    # Download a cutout of a WISE band as 1 FITS image:
    image_url = (
        "http://irsa.ipac.caltech.edu/ibe/data/wise/allsky/4band_p1bm_frm/6a/02206a"
        + "/149/02206a149-w1-int-1b.fits?center=70,20&size=200pix"
    )
    filename = download_file(image_url, cache=True, timeout=120)
    # Download a 2MASS catalog using an IRSA VO Table Access Protocol ([TAP](https://irsa.ipac.caltech.edu/docs/program_interface/astropy_TAP.html)) search:
    table_url = (
        "http://irsa.ipac.caltech.edu/TAP/sync?FORMAT=IPAC_TABLE&"
        + "QUERY=SELECT+*+FROM+fp_psc+WHERE+CONTAINS(POINT('J2000',ra,dec),"
        + "CIRCLE('J2000',70.0,20.0,0.1))=1"
    )
    tablename = download_file(table_url, timeout=120, cache=True)
    # ## Display Tables and Catalogs
    # Instantiating FireflyClient should open a browser to the firefly server in a new tab. You can also achieve this using the following method. The browser open only works when running the notebook locally, otherwise a link is displayed.
    # localbrowser, browser_url = fc.launch_browser()
    # If it does not open automatically, try using the following command to display a web browser link to click on:
    fc.display_url()
    # Alternatively, uncomment the lines below (while commenting out the 2 lines above) to display the browser application in the notebook:
    # from IPython.display import IFrame
    # print('url: %s' % fc.get_firefly_url())
    # IFrame(fc.get_firefly_url(), 1100, 1000)
    # The current example involves 2 images in FITS format to be viewed through the chosen browser, both in different ways.
    # For the 1st method, upload a local file to the server and then display it:
    imval = fc.upload_file(filename)
    status = fc.show_fits(
        file_on_server=imval, plot_id="wise-cutout", title="WISE Cutout"
    )
    assert status is not None
    # For the 2nd method, pull an image directly from a URL:
    status = fc.show_fits(
        file_on_server=None,
        plot_id="wise-fullimage",
        URL="http://irsa.ipac.caltech.edu/ibe/data/wise/allsky/4band_p1bm_frm/6a/02206a"
        + "/149/02206a149-w1-int-1b.fits",
    )
    # Upload a catalog table (with coordinates) to the server so it will overlay the image with markers by default. Note that markers can be visible on both "wise-cutout" and "wise-fullimage" since they would include the same field of view:
    file = fc.upload_file(tablename)
    status = fc.show_table(
        file, tbl_id="tablemass", title="My 2MASS Catalog", page_size=50
    )
    # Add an xy plot using the uploaded table data:
    status = fc.show_xyplot(tbl_id="tablemass", xCol="j_m", yCol="h_m-k_m")
    # Alternatively, more generic method show_chart() can be used to create the same plot
    # trace0 = {'tbl_id': 'tablemass', 'x': "tables::j_m", 'y': "tables::h_m-k_m",
    #           'type' : 'scatter', 'mode': 'markers'}
    # status = fc.show_chart(data=[trace0])
    # Zoom into the full image by a factor of 2 (note the `plot_id` parameter we used earlier)
    status = fc.set_zoom("wise-fullimage", 2)
    # Pan the full image to center on a given celestial coordinate:
    status = fc.set_pan("wise-fullimage", x=70, y=20, coord="J2000")
    # Set the stretch for the full image based on IRAF zscale interval with a linear algorithm:
    status = fc.set_stretch("wise-fullimage", stype="zscale", algorithm="linear")
    # Change color of the image:
    status = fc.set_color("wise-fullimage", colormap_id=6, bias=0.6, contrast=1.5)
    # Add region data to the cutout image (2 areas to begin with):
    my_regions = [
        "image;polygon 125 25 160 195 150 150 #color=cyan",
        "icrs;circle 69.95d 20d 30i # color=orange text={region 5/7}",
    ]
    status = fc.add_region_data(
        region_data=my_regions, region_layer_id="layer1", plot_id="wise-cutout"
    )
    # Remove the second region while keeping the first one visible:
    fc.remove_region_data(region_data=my_regions[1], region_layer_id="layer1")
