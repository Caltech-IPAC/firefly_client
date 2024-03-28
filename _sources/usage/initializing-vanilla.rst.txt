#####################################
Initializing a FireflyClient instance
#####################################

Once a Firefly server has been identified, the connection parameters can be
used to initialize a :class:`FireflyClient` instance. By default, the value
of the environment variable `FIREFLY_URL` will be used as the server URL, if defined. If
`FIREFLY_URL` is not defined, the default server URL is `http://localhost:8080/firefly`
which is often used for a Firefly server running locally.

Optional arguments for initializing a `FireflyClient` instance include `channel`
and `html_file`.

For a default server running locally, use `localhost` or `127.0.0.1` together
with the port that the server is using, and append `/firefly`. The default port is 8080.

.. code-block:: py
    :name: using-localhost

    import firefly_client
    fc = firefly_client.FireflyClient('http://127.0.0.1:8080/firefly')

If the Python session is running on your own machine, you can use the
:meth:`FireflyClient.launch_browser` method to open up a browser tab.

.. code-block:: py
    :name: launch-browser

    fc.launch_browser()

The :meth:`FireflyClient.launch_browser` method will return two values: a boolean
indicating whether the web browser open was successful, and the URL for your
web browser.

.. warning::

    On Mac OS X 10.12.5, an error message may be displayed with a URL and
    a note that it doesn't understand the "open location message". If a
    browser tab is not automatically opened, copy and paste the displayed
    URL into the address bar of your browser. This issue has been fixed
    in Mac OS X 10.12.6.

If your Python session is not running on your local machine, the
:meth:`FireflyClient.launch_browser`
method will display the URL for your web browser. Alternatively, you can use
the :meth:`FireflyClient.display_url` method to print the browser URL if
running in a terminal, and to show a clickable link if running in a
Jupyter notebook.

.. code-block:: py

    fc.display_url()

In typical usage, it is unnecessary to set the `channel` parameter when
instantiating `FireflyClient`. A unique string will be auto-generated.
If you do wish to set the channel explicitly, e.g. for sharing your display
with someone else, take care to make the channel unique.

.. warning::

    After initializing :class:`FireflyClient`, make sure you have opened a web browser
    to the appropriate URL, before proceeding to use the Python API described
    in the following sections.


Initializing with the make_client Factory Function
--------------------------------------------------

For an easier initialization, you can use the :meth:`FireflyClient.make_client`
factor function. This function will use the value of the FIREFLY_URL
environment variable for the Firefly server. Additionally, it will attempt
to start a Firefly browser tab or window if possible, and if not, it will
display a link for the Firefly display.

.. code-block:: py

    fc = FireflyClient.make_client()


