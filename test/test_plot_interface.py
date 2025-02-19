#!/usr/bin/env python
# coding: utf-8

# This notebook demonstrates the simplified plot interface. The philosophy of the `plot` module is similar to how `import matplotlib.pyplot as plt` is used to select a backend and make simple plotting commands available, with the object-oriented interface still available for advanced applications.

# The goal of the notebook is to easily show tables, make plots, and display images. The data items can be uploaded directly as files to Firefly, or as objects with serialization methods.

# ## Initialize Firefly viewer

# When the plot method is imported, a search will be conducted for an instance of `FireflyClient`:
# 
# * If the current session includes an operational instance of `FireflyClient` with a web browser connected, it will be used.
# * Else, if the environment variable `FIREFLY_URL` is defined, an instance of `FireflyClient` will be created using that URL.
# * Else, if there is a Firefly server running locally at `http://localhost:8080/firefly`, it will be used.
# * Finally, a short list of public servers will be tried.

# In[19]:


from firefly_client import FireflyClient
import firefly_client.plot as ffplt

fc = FireflyClient.make_client("https://irsa.ipac.caltech.edu/irsaviewer")
ffplt.use_client(fc)


# The next cell will attempt to launch a browser, if there is not already a web page connected to the instance of `FireflyClient`.

# In[2]:


ffplt.open_browser()


# If the browser launch is unsuccessful, a link will be displayed for your web browser.

# The next cell will display a clickable link

# In[3]:


ffplt.display_url()


# #### Optional: specifying a server and channel.
# 
# By default, a channel is generated for you. If you find it more convenient to use a specific server and channel, uncomment out the next cell to generate a channel from your username.

# In[4]:


# import os
# my_channel = os.environ['USER'] + '-plot-module'
# ffplt.reset_server(url='https://lsst-demo.ncsa.illinois.edu/firefly', channel=my_channel)


# ## Restart here

# If needed, clear the viewer and reset the layout to the defaults.

# In[20]:


ffplt.clear()


# In[21]:


ffplt.reset_layout()


# ### Upload a table directly from disk.

# In[22]:


import astropy.utils.data


# For the case of a file already on disk, pass the path and a title for the table. Here we download a file.

# In[23]:


m31_table_fname = astropy.utils.data.download_file(
    "http://web.ipac.caltech.edu/staff/roby/demo/m31-2mass-2412-row.tbl",
    timeout=120,
    cache=True,
)


# Upload the table file from disk, and enable the coverage image

# In[24]:


tbl_id = ffplt.upload_table(m31_table_fname, title="M31 2MASS", view_coverage=True)


# Make a histogram from the last uploaded table, with the minimum required parameters

# In[25]:


ffplt.hist("j_m")


# Make a scatter plot from the last uploaded table, with the minimum required parameters

# In[26]:


ffplt.scatter("h_m - k_m", "j_m")


# ### Viewing a Python image object

# Load a FITS file using astropy.io.fits

# In[12]:


import astropy.io.fits as fits

m31_image_fname = astropy.utils.data.download_file(
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


wise_tbl_name = astropy.utils.data.download_file(
    "http://web.ipac.caltech.edu/staff/roby/demo/WiseDemoTable.tbl",
    timeout=120,
    cache=True,
)


# Read the downloaded table in IPAC table format

# In[17]:


from astropy.table import Table

wise_table = Table.read(wise_tbl_name, format="ipac")


# Upload to the viewer with a set title

# In[18]:


ffplt.upload_table(wise_table, title="WISE Demo Table")


# In[ ]:





# In[ ]:




