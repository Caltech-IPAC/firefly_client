#!/usr/bin/env python
# coding: utf-8

# # Intro

# This notebook demonstrates basic usage of the firefly_client API method `overlay_footprints` which overlays the footprint described in image pixel of JSON format on a FITS image.
# 
# Note that it may be necessary to wait for some cells (like those displaying an table) to complete before executing later cells.

# ## Setup

# Imports for firefly_client: 

# In[ ]:


from firefly_client import FireflyClient
import astropy.utils.data

using_lab = False
url = "http://127.0.0.1:8080/firefly"
# FireflyClient._debug= True


# In this example, we use local firefly server (you can also use public server - irsaviewer instead):

# Instantiate `FireflyClient` using the url above.

# In[ ]:


fc = FireflyClient.make_lab_client() if using_lab else FireflyClient.make_client(url)


# ## Start with Image Data

# The data used in this example are taken from http://web.ipac.caltech.edu/staff/shupe/firefly_testdata and can be downloaded. Download a file using the image URL below and upload it to the server:

# In[ ]:


image_url = (
    "http://web.ipac.caltech.edu/staff/shupe/firefly_testdata/calexp-subset-HSC-R.fits"
)
filename = astropy.utils.data.download_file(image_url, cache=True, timeout=120)
imval = fc.upload_file(filename)


# Set the `plot_id` for the image and display it through the opened browser:

# In[ ]:


plotid = "footprinttest"
status = fc.show_fits(
    file_on_server=imval, plot_id=plotid, title="footprints HSC R-band"
)


# ## Add Data for Footprints

# Upload a table with footprint data using the foloowing url from where it can be downloaded:

# In[ ]:


table_url = "http://web.ipac.caltech.edu/staff/shupe/firefly_testdata/footprints-subset-HSC-R.xml"
footprint_table = astropy.utils.data.download_file(table_url, cache=True, timeout=120)
tableval = fc.upload_file(footprint_table)


# Overlay a footprint layer (while comparing a highlighted section to the overall footprint) onto the plot using the above table:

# In[ ]:


status = fc.overlay_footprints(
    tableval,
    title="footprints HSC R-band",
    footprint_layer_id="footprint_layer_1",
    plot_id=plotid,
    highlightColor="yellow",
    selectColor="cyan",
    style="fill",
    color="rgba(74,144,226,0.30)",
)

