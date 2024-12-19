#################
Displaying Images
#################

Since Firefly was originally developed to visualize data products from
astronomical archives, displaying an image is a two-step process of
uploading a file and then showing it. The examples here use the data
products downloaded in :ref:`firefly_client-getting-started`.

The :meth:`FireflyClient.upload_file` method uploads the file and
returns a location understood by the Firefly server. The location
string is passed to :meth:`FireflyClient.show_fits` to display
the image. In the display step,
it is recommended to explicitly specify the `plot_id` parameter
for later use in modifying the image display.

.. code-block:: py

    fval = fc.upload_file('2mass-m31-green.fits')
    fc.show_fits(fval, plot_id='m31-green', title='2MASS H, M31')


Modifying an Image Display
--------------------------

Zooming, panning, and changing the stretch (mapping of pixels to display
values) is accomplished by corresponding methods, passing in the `plot_id`
as the first argument.

.. code-block:: py

    fc.set_zoom('m31-green', 4)
    fc.set_pan('m31-green', 200, 195)
    fc.set_stretch('m31-green', 'sigma', 'log', lower_value=-2, upper_value=30)

A "zscale" stretch may be commanded with alternate parameters:

.. code-block:: py

    fc.set_stretch('m31-green', 'zscale', 'linear')

At present the API does not include a function for changing the color map
for the image. The relevant Javascript action may be invoked using
:meth:`FireflyClient.dispatch`:

.. code-block:: py

    fc.dispatch(action_type='ImagePlotCntlr.ColorChange',
                payload={'plotId': 'm31-green',
                'cbarId': 16})

The colormap can be reverted to the original grayscale by using the
command above together with `'cbarId' : 0`.


Specifying Zoom and Stretch Values When First Displaying an Image
-----------------------------------------------------------------

It is often advantageous to specify the zoom, stretch, and color table
parameters in the same command that displays the image, to avoid problems
with the later commands being ignored when the image display has not completed.


To specify the stretch as part of the image display, you can generate
a range values string. This example is for an asinh stretch with a Q
value of 6 and an upper level of 98 percent:

.. code-block:: py

    rvstring = fc._create_rangevalues_standard(algorithm='asinh',
                                               asinh_q_value=6,
                                               upper_value=98.0)

The zoom value can be
specified in several different ways. When displaying images with different
pixel scales, the best practice is to specify
`ZoomType='ARCSEC_PER_SCREEN_PIX'` and then the numerical value,
e.g. `ZoomArcsecPerScreenPix=0.3`.

The color table is specified with an integer. The pan point can be
specified with parameter `WorldPt`. For example:

.. code-block:: py

    size_in_arcsec = 400
    ra = 150.00983
    dec = 2.59783
    target = '{};{};EQ_J2000'.format(ra, dec)
    fc.show_fits(plot_id='IRAC1',
                 Title='COSMOS 3.6um',
                 Type='SERVICE',
                 Service='ATLAS',
                 SurveyKey='cosmos.cosmos_irac',
                 SurveyKeyBand='IRAC1',
                 WorldPt=target,
                 SizeInDeg=size_in_arcsec/3600,
                 ColorTable=1,
                 ZoomType='ARCSEC_PER_SCREEN_PIX',
                 ZoomArcsecPerScreenPix=0.3,
                 RangeValues=rvstring)

Turning On WCS Locking
----------------------

When multiple images covering the same sky location are displayed, you can
align and lock by sky coordinates. To lock and align by world coordinates:

.. code-block:: py

    fc.align_images(lock_match=True)

Retrieving Images Using IRSA-Specific Searches
----------------------------------------------

Firefly includes image search processors for Infrared Science Archive (IRSA)
image holdings. A table of available projects for image searches is
maintained in the Firefly code base. The information can be retrieved
into an Astropy table:

.. code-block:: py

    from astropy.table import Table
    surveys = Table.read('https://raw.githubusercontent.com/Caltech-IPAC/firefly/dev/src/firefly/' +
                         'java/edu/caltech/ipac/firefly/resources/irsa-image-master-table.csv',
                         format='csv')

To select images available for the COSMOS project:

.. code-block:: py

    cosmos_surveys = surveys[surveys['missionId'] == 'COSMOS']

To search the survey:

.. code-block:: py

    size_in_arcsec = 200
    ra = 150.00983
    dec = 2.59783
    target = '{};{};EQ_J2000'.format(ra, dec)
    fc.show_fits(plot_id='IRAC1',
                 Title='COSMOS 3.6um',
                 Type='SERVICE',
                 Service='ATLAS',
                 SurveyKey='cosmos.cosmos_irac',
                 SurveyKeyBand='IRAC1',
                 WorldPt=target,
                 SizeInDeg=size_in_arcsec/3600,
                 ColorTable=1,
                 ZoomType='ARCSEC_PER_SCREEN_PIX',
                 ZoomArcsecPerScreenPix=0.3,
                 RangeValues=rvstring)


Displaying HiPS Images
----------------------

While the above examples involve displaying FITS images, it's also possible to view a HiPS image using a different method that involves specifying the base URL where the target search is performed. 
To search the survey:

.. code-block:: py

    hips_url = 'https://irsa.ipac.caltech.edu/data/hips/CDS/2MASS/Color/'
    size_in_deg = 0.2
    ra = 274.700727
    dec = -13.807228
    target = '{};{};EQ_J2000'.format(ra, dec)
    fc.show_hips(viewer_id='hipspc1',
                 plot_id='HipsID1-1',
                 hips_root_url = hips_url,
                 Title='HiPS-2m',
                 WorldPt=target,
                 SizeInDeg=size_in_deg)


Displaying 3-Color Images
-------------------------

It is possible to create a 3-color composite image using a list of dictionaries containing included parameters on all given bands (or simply one dictionary for that band). For example: 

.. code-block:: py

    rv = '92,-2,92,8,NaN,2,44,25,600,120'
    ra = 210.80227
    dec = 54.34895
    target = '{};{};EQ_J2000'.format(ra, dec)
    threeC= [
         {
             'Type'      : 'SERVICE',
             'Service'   : 'WISE',
             'Title'     : '3 color',
             'SurveyKey'  : '3a',
             'SurveyKeyBand': '3',
             'WorldPt'    : target,
             'RangeValues': rv,
             'SizeInDeg'  : '.14'
         },
         {
             'Type'      : 'SERVICE',
             'Service'   : 'WISE',
             'Title'     : '3 color',
             'SurveyKey'  : '3a',
             'SurveyKeyBand': '2',
             'WorldPt'    : target,
             'RangeValues': rv,
             'SizeInDeg'  : '.14'
         },
         {
             'Type'      : 'SERVICE',
             'Service'   : 'WISE',
             'Title'     : '3 color',
             'SurveyKey'  : '3a',
             'SurveyKeyBand': '1',
             'WorldPt'    : target,
             'RangeValues': rv,
             'SizeInDeg'  : '.14'
         }]
    fc.show_fits_3color(threeC,
    plot_id='wise_m101',
    viewer_id='3C')


Displaying Image from a URL
---------------------------

If you have the URL of an image, you can pass it directly instead of 
downloading it and then uploading it to firefly:

.. code-block:: py

    image_url = 'http://irsa.ipac.caltech.edu/ibe/data/wise/allsky/4band_p1bm_frm/6a/02206a/149/02206a149-w1-int-1b.fits?center=70,20&size=200pix'
    fc.show_fits(url=image_url, plot_id='wise-allsky', title='WISE all-sky')
