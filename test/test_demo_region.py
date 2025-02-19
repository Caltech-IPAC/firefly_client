#!/usr/bin/env python
# coding: utf-8

# # Intro

# This notebook demonstrates basic usage of the firefly_client API involving how to add region data with text to a FITS image.
# 
# Note that it may be necessary to wait for some cells (like those displaying an image) to complete before executing later cells.

# ## Setup

# Imports for firefly_client:

# In[ ]:


from firefly_client import FireflyClient
import astropy.utils.data

using_lab = False
url = "http://127.0.0.1:8080/firefly"
# FireflyClient._debug= True


# In this example, we use the IRSA Viewer application for firefly server:

# Instantiate `FireflyClient` using the URL above:

# In[ ]:


fc = FireflyClient.make_lab_client() if using_lab else FireflyClient.make_client(url)


# ## Download some data

# Download a sample image and table.
# 
# We use astropy here for convenience, but firefly_client itself does not depend on astropy.

# Download a cutout of a WISE band as 1 FITS image:

# In[ ]:


image_url = (
    "http://irsa.ipac.caltech.edu/ibe/data/wise/allsky/4band_p1bm_frm/6a/02206a"
    + "/149/02206a149-w1-int-1b.fits?center=70,20&size=200pix"
)
filename = astropy.utils.data.download_file(image_url, cache=True, timeout=120)


# ## Display tables and catalogs

# Instantiating FireflyClient should open a browser to the firefly server in a new tab. You can also achieve this using the following method. The browser open only works when running the notebook locally, otherwise a link is displayed.

# In[ ]:


# localbrowser, browser_url = fc.launch_browser()


# If it does not open automatically, try using the following command to display a web browser link to click on:

# In[ ]:


fc.display_url()


# Upload a local file to the server and then display it (while keeping in mind the `plot_id` parameter being chosen):

# In[ ]:


imval = fc.upload_file(filename)
status = fc.show_fits(
    file_on_server=imval, plot_id="region test", title="text region test"
)


# Add region data containing text region with 'textangle' property

# In[ ]:


text_regions = [
    'image;text 100 150 # color=pink text={text angle is 30 deg } edit=0 highlite=0  font="Times 16 bold normal" textangle=30',
    'image;text 100 25 # color=pink text={text angle is -20 deg } font="Times 16 bold italic" textangle=-20',
    "circle  80.48446937 77.231180603 13.9268922 #  text={physical;circle ;; color=cyan } color=cyan",
    "image;box 100 150 60 30 30 # color=red text={box on # J2000 with size w=60 & h=30}",
    "circle  80.484469p 77.231180p 3.002392 # color=#B8E986 text={This message has both a \" and ' in it}",
]
status = fc.add_region_data(
    region_data=text_regions, region_layer_id="layerTextRegion", plot_id="region test"
)

