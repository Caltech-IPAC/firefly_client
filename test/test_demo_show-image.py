#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from firefly_client import FireflyClient

using_lab = False
url = "http://127.0.0.1:8080/firefly"
# FireflyClient._debug= True


# In[ ]:


fc = FireflyClient.make_lab_client() if using_lab else FireflyClient.make_client(url)


# In[ ]:


fc.show_fits(URL="http://web.ipac.caltech.edu/staff/roby/demo/wise-m51-band2.fits")

