"""
Module of firefly_client.py
--------------------------
This module defines class 'FireflyClient' and methods to remotely communicate to Firefly viewer
by dispatching remote actions.
"""
import io
import re
import requests
import webbrowser
import json
import time
import socket
from urllib.parse import urljoin
import math
import weakref
import os
from copy import copy


try:
    from .ffws import FFWs
except ImportError:
    from ffws import FFWs
try:
    from .env import Env
except ImportError:
    from env import Env
try:
    from .range_values import RangeValues
except ImportError:
    from range_values import RangeValues
try:
    from .fc_utils import debug, warn, dict_to_str, create_image_url, ensure3, gen_item_id,\
        DebugMarker, ALL, ACTION_DICT, LO_VIEW_DICT
except ImportError:
    from fc_utils import debug, warn, dict_to_str, create_image_url, ensure3, gen_item_id,\
        DebugMarker, ALL, ACTION_DICT, LO_VIEW_DICT

__docformat__ = 'restructuredtext'
_def_html_file = Env.find_default_firefly_html()
_default_url = Env.find_default_firefly_url()

BROWSER = 'browser'
LAB = 'lab'
UNKNOWN = 'UNKNOWN'


class FireflyClient:
    """
    For Firefly client to build interface to remotely communicate to the Firefly viewer.

    Parameters
    ----------
    url : `str`
        URL for Firefly server, e.g. https://lsst-demo.ncsa.illinois.edu/firefly.
        Defaults to the value of the environment variable FIREFLY_URL, if defined;
        or to 'http://localhost:8080/firefly' if FIREFLY_URL is not defined.
    channel : `str`
        WebSocket channel ID. Default is None which auto-generates a unique string.
    html_file : `str`
        HTML file that is the 'landing page' for users, appended to the URL.
        Defaults to ''. If the landing page in 'slate.html' it puts FireflyClient into slate mode.
    make_default : `bool`
        If True, make this the default FireflyClient instance. Default False.
    use_lab_env : `bool`
        If True, try to use environment variables for Jupyterlab. This can only be True in the
        Jupyter lab environment, otherwise there is an error. Default False.
    start_tab: `bool`
        If True, bring up a Jupyterlab or a browser tab for Firefly. Default False.
    start_browser_tab: `bool`
        If True, and start_tab is true and in use_lab_env is true then start a browser tab. Default False.
    token: `str` or None
        A token for connecting to a Firefly server that requires
        authentication. The provided token will be appended to the
        string "Bearer " to form the value of the "Authorization" header
        in the sessions attribute.
    """

    TAB_ID = 'firefly-viewer-tab-id'
    TRIVIEW_ICov_Ch_T = 'TRIVIEW_ICov_Ch_T'
    TRIVIEW_I_ChCov_T = 'TRIVIEW_I_ChCov_T'
    BIVIEW_ICov_Ch = 'BIVIEW_ICov_Ch'
    BIVIEW_I_ChCov = 'BIVIEW_I_ChCov'
    BIVIEW_T_IChCov = 'BIVIEW_T_IChCov'
    BIVIEW_IChCov_T = 'BIVIEW_IChCov_T'
    tri_view_types_list = [
        TRIVIEW_ICov_Ch_T,
        TRIVIEW_I_ChCov_T,
        BIVIEW_ICov_Ch,
        BIVIEW_I_ChCov,
        BIVIEW_T_IChCov,
        BIVIEW_IChCov_T
    ]

    tri_view_layout_desc = {
        TRIVIEW_ICov_Ch_T: 'top left: image/cov, top right: charts, bottom: tables',
        TRIVIEW_I_ChCov_T: 'top left: image, top right: charts/cov, bottom: tables',
        BIVIEW_ICov_Ch: 'left: image/cov, right: charts',
        BIVIEW_I_ChCov: 'left: image, right: charts/cov',
        BIVIEW_T_IChCov: 'left: tables, right: image/charts/cov',
        BIVIEW_IChCov_T: 'left: image/charts/cov, right: tables',
    }

    # viewer modes
    TRIVIEW_VIEWER = 'FireflyViewer'
    SLATE_VIEWER = 'FireflySlate'
    NO_VIEWER = 'NO_VIEWER'
    _viewer_modes = [TRIVIEW_VIEWER,SLATE_VIEWER,NO_VIEWER]

    # viewer ids
    PINNED_CHART_VIEWER_ID = 'PINNED_CHART_VIEWER_ID'
    PINNED_IMAGE_VIEWER_ID = 'DEFAULT_FITS_VIEWER_ID'

    _debug = False
    # Keep track of instances.
    instances = []

    """All events are enabled for the listener (`str`)."""

    # id for table, region layer, extension
    _item_id = {'Table': 0, 'RegionLayer': 0, 'Extension': 0, 'MaskLayer': 0, 'XYPlot': 0,
                'Cell': 0, 'Histogram': 0, 'Plotly': 0, 'Image': 0, 'FootprintLayer': 0}

    @classmethod
    def make_lab_client(cls, start_browser_tab=False, html_file=_def_html_file, start_tab=True,
                        verbose=False, token=None):
        """
        Factory method to create a Firefly client in the Jupyterlab environment.
        If you are using Jupyterlab with the jupyter_firefly_extension installed,
        then this method is the best way to construct a FireflyClient.
        If called in a non-Jupyterlab  environment, the method raises a RuntimeError.

        Parameters
        ----------
        start_browser_tab : `bool`
            If True start a browser tab, if False start a lab tab. start_tab must
            also be True.
            To start a new tab you will have to disable popup blocking for the Jupyterlab site.
                Chrome: look at the right side of the address bar
                Firefox: a preference bar appears at the top
                Safari: shows an animation to follow on the left side bar
        html_file: `str`, optional
            HTML file that is the 'landing page' for users, appended to the URL.
            Defaults to the value of the environment variable 'FIREFLY_URL' if
            it is defined: otherwise defaults to ''.
            If the landing page in 'slate.html' it puts FireflyClient into slate mode.
        start_tab: `bool`, optional
            If True, bring up a Jupyterlab or a browser tab for Firefly. You should almost always take the default.
        token: `str` or None
            A token for connecting to a Firefly server that requires
            authentication. The provided token will be appended to the
            string "Bearer " to form the value of the "Authorization" header
            in the sessions attribute.
        verbose: `boolean`
            If True, print instructions if web browser is not opened (default *false*)

        Returns
        -------
        out : `FireflyClient`
            A FireflyClient that works in the lab environment
        """
        tab_type = BROWSER if (start_browser_tab and start_tab) else (LAB if start_tab else None)
        url, channel = Env.validate_lab_client(tab_type == BROWSER)
        fc = cls(url, channel, html_file, token)
        if tab_type:
            verbose and tab_type == BROWSER and Env.show_start_browser_tab_msg(fc.get_firefly_url())
            fc._lab_env_tab_start(tab_type, html_file)
        return fc

    @classmethod
    def make_client(cls, url=_default_url, html_file=_def_html_file, launch_browser=True,
                    channel_override=None, verbose=False, token=None, viewer_override=None):
        """
        Factory method to create a Firefly client in a plain Python, IPython, or
        notebook session, and attempt to open a display.  If a display cannot be
        opened, a link will be displayed.

        Parameters
        ----------
        url: `str`, optional
            URL of the Firefly server. The default is determined by checking
            environment variables 'fireflyURLLab' and 'FIREFLY_URL'; if these
            are undefined, then the default is 'http://localhost:8080/firefly'
            for the case of a user running a Firefly server on their desktop.
        html_file: `str`, optional
            HTML file that is the 'landing page' for users, appended to the URL.
            Defaults to the value of the environment variable 'FIREFLY_URL' if
            it is defined: otherwise defaults to ''.
            If the landing page in 'slate.html' it puts FireflyClient into slate mode.
        launch_browser: `bool`, optional
            If True, attempt to launch a browser tab for the Firefly viewer.
            If that attempt is unsuccessful, a link for the Firefly viewer is
            displayed.
        channel_override: `str` or None
            If channel_override is None, the value of the environment variable
            'FIREFLY_CHANNEL' is checked. If unset, then a URL-safe channel
            string is generated.
            If channel_override is set to a string, it is used for the Firefly
            channel.
        verbose: `bool`
            If True, print instructions if web browser is not opened (default *false*)
        token: `str` or None
            A token for connecting to a Firefly server that requires
            authentication. The provided token will be appended to the
            string "Bearer " to form the value of the "Authorization" header
            in the sessions attribute.
        viewer_override: `str`
            This parameter is almost never used, default to None.
            It is only for those special circumstances that you would use
            firefly_client to control a custom created interface that is not a triview ora slate view.
            maybe one of FireflyClient.TRIVIEW_VIEWER, FireflyClient.SLATE_VIEWER, FireflyClient.NO_VIEWER,

        Returns
        -------
        fc : `FireflyClient`
            A FireflyClient that works in the lab environment
        """
        fc = cls(url, Env.resolve_client_channel(channel_override), html_file, token, viewer_override)
        verbose and Env.show_start_browser_tab_msg(fc.get_firefly_url())
        launch_browser and fc.launch_browser()
        return fc

    def __init__(self, url, channel, html_file=_def_html_file, token=None, viewer_override=None):
        DebugMarker.firefly_client_debug = FireflyClient._debug
        FireflyClient.instances.append(weakref.ref(self))

        ssl = url.startswith('https://')
        self.wsproto = 'wss' if ssl else 'ws'
        self.location = url[8:] if ssl else url[7:]
        self.location = self.location[:-1] if self.location.endswith('/') else self.location
        self.url = url
        self.channel = channel
        self.render_tree_id = None
        self.auth_headers = {'Authorization': 'Bearer {}'.format(token)} if token and ssl else None
        self.header_from_ws = {'FF-channel': channel}
        self.lab_env_tab_type = UNKNOWN

        # urls for cmd service and browser
        protocol = 'https' if ssl else 'http'
        self.url_cmd_service = urljoin('{}://{}/'.format(protocol, self.location), 'sticky/CmdSrv')
        self.url_browser = urljoin(urljoin('{}://{}/'.format(protocol, self.location), html_file), '?__wsch=')
        self.url_bw = self.url_browser  # keep around for backward compatibility

        self.session = requests.Session()
        token and ssl and self.session.headers.update(self.auth_headers)
        not ssl and token and warn('token ignored: should be None when url starts with http://')
        self.firefly_viewer = FireflyClient.get_viewer_mode(html_file,viewer_override)

        access = FireflyClient.confirm_access(url, token)
        if not access['success']:
            debug(f'Failed to access url: {url}, with token: {token}\n'
                  f'Response status: {access["response"].status_code} ({access["response"].reason})\n'
                  f'Response headers: {dict_to_str(access["response"].headers)}\n'
                  f'Response text: {access["response"].text}')
            url_err_msg = Env.failed_net_message(url, access['response'].status_code)
            token_err_msg = (
                'Check if the passed `token` is valid and has the necessary '
                'authorization to access the above URL.'
                if token else
                'If an authorization token is required to access the above URL, '
                'the `token` parameter must be passed.'
            )
            raise ValueError(f'{url_err_msg}\n\n{token_err_msg}')
        debug(f'new instance: {url}')

    def _lab_env_tab_start(self, tab_type, html_file):
        """start a tab in the lab environment, tab_type must be 'lab' or 'browser' """
        self.lab_env_tab_type = tab_type
        if tab_type == BROWSER:
            idx = self.channel.find('__viewer')
            c = self.channel[0:idx] if idx > -1 else self.channel  # the ext will add '__viewer' so I have to remove it
            self.dispatch(ACTION_DICT['StartBrowserTab'],
                          {'channel': c, 'fireflyHtmlFile': _def_html_file}, Env.firefly_channel_lab)
        elif tab_type == LAB:
            if not self.render_tree_id:
                self.render_tree_id = FireflyClient.TAB_ID  # no longer generating redner_tree_id
                # self.render_tree_id = 'slateClient-%s-%s' % (len(self.instances), round(time.time()))
            self.show_lab_tab(html_file)

    def show_lab_tab(self, html_file=_def_html_file):
        """If using a jupyter lab tab - show it or reopen it. If not using a lab tab then noop"""
        self.lab_env_tab_type = (LAB and
                                 self.dispatch(ACTION_DICT['StartLabWindow'],
                                               {'fireflyHtmlFile': html_file}))

    @staticmethod
    def get_viewer_mode(html_file, viewer_override):
        if viewer_override:
            if viewer_override in FireflyClient._viewer_modes:
                return viewer_override
            else:
                warn('viewer_override mode: {} is not a recognized mode, using {}'.format(viewer_override, UNKNOWN))
                return UNKNOWN
        else:
            return FireflyClient.SLATE_VIEWER if html_file == 'slate.html' else FireflyClient.TRIVIEW_VIEWER
        
    @staticmethod
    def confirm_access(url, token=None):
        headers = {'Authorization': f'Bearer {token}'} if token else None
        healthz_url = url + ('healthz' if url.endswith('/') else '/healthz')
        # disable redirects that may happen in the absence of a token
        response = requests.get(healthz_url, headers=headers, allow_redirects=False)
        return {'success': response.status_code == 200, 'response': response}

    def _send_url_as_get(self, url):
        return self.call_response(self.session.get(url, headers=self.header_from_ws))

    def _send_url_as_post(self, data):
        return self.call_response(self.session.post(self.url_cmd_service, data=data, headers=self.header_from_ws))

    def call_response(self, response):
        if response.status_code != 200:
            raise ValueError(Env.failed_net_message(self.url, response.status_code))
        try:
            status = json.loads(response.text)
            return status[0]
        except ValueError as err:
            warn('JSON parsing Error:')
            if len(response.text) > 300:
                warn('Response string (first 300 characters):\n' + response.text[0:300])
                debug('Full Response:\n' + response.text)
            else:
                warn('Response string:\n' + response.text[0:300])

            raise err
    
    @staticmethod
    def _get_ip():
        """Find local IP address, based on https://stackoverflow.com/q/166506/8252556."""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 1)) # doesn't even have to be reachable
            ip = s.getsockname()[0]
        except Exception:
            ip = '127.0.0.1'
        finally:
            s.close()
        return ip

    def _is_page_connected(self):
        """Check if the page is connected."""
        url = f'{self.url_cmd_service}?cmd=pushAliveCheck&ipAddress={self._get_ip()}'
        retval = self._send_url_as_get(url)
        return retval['active']

    def is_triview(self): return self.firefly_viewer == FireflyClient.TRIVIEW_VIEWER

    def is_slate(self): return self.firefly_viewer == FireflyClient.SLATE_VIEWER

    @staticmethod
    def _make_pid_param(plot_id):
        return ','.join(plot_id) if isinstance(plot_id, list) else plot_id

# -----------------------------------------------------------------
# -----------------------------------------------------------------
# Public API Begins
# -----------------------------------------------------------------
# -----------------------------------------------------------------
    def add_listener(self, callback, name=ALL):
        """
        Add a callback function to listen for events on the Firefly client.

        Parameters
        ----------
        callback : `Function`
            The function to be called when a event happens on the Firefly client.
        name : `str`, optional
            The name of the events (the default is `ALL`, all events).

        Returns
        -------
        out : none

        """
        try:
            def header_cb(headers): self.header_from_ws = headers
            FFWs.add_listener(self.wsproto, self.auth_headers, self.channel, self.location, callback, name, header_cb)
        except ConnectionRefusedError as err:
            raise ValueError(f"Couldn't add listener: {err}") from err

    def remove_listener(self, callback, name=ALL):
        """
        Remove an event name from the callback listener.

        Parameters
        ----------
        callback : `Function`
            A previously set callback function.
        name : `str`, optional
            The name of the event to be removed from the callback listener
            (the default is `ALL`, all events).

        Returns
        -------
        out : none

        .. note:: `callback` in the listener list is removed if all events are removed from the callback.
        """
        FFWs.remove_listener(self.channel, self.location, callback, name)

    def wait_for_events(self):
        """
        Wait over events from the server.

        Pause and do not exit.

        This is optional. You should not use this method in ipython notebook.
        Event will get called anyway.
        """
        FFWs.wait_for_events(self.channel, self.location)

    def disconnect(self):
        """DEPRECATED. Now just remove the listeners. Disconnect the WebSocket.
        """
        FFWs.close_ws_connection(self.channel, self.location)

    def get_firefly_url(self, channel=None):
        """
        Get URL to Firefly Tools viewer and the channel set.
        Normally this method will be called without any parameters.

        Parameters
        -------------
        channel : `str`, optional
            A different channel string than the default.

        Returns
        -------
        out : `str`
            url string.
        """
        return self.url_browser + (self.channel if channel is None else channel)

    def display_url(self, url=None):
        """
        Display URL in a user-friendly format

        Parameters
        ----------
        url : `str`, optional
            A url overriding the default (the default retrieves from *self.get_firefly_url*).
        """
        if url is None:
            url = self.get_firefly_url()
        try:
            ipy_str = str(type(get_ipython()))
        except NameError:
            ipy_str = ''
        if 'zmqshell' in ipy_str:
            from IPython.display import display, HTML
            display(HTML('Open your web browser to <a href="{}"" target="_blank">this link</a>'.format(url)))
        else:
            print('Open your web browser to {}'.format(url))

    def launch_browser(self, channel=None, force=False, verbose=True):
        """
        Launch a browser with the Firefly Tools viewer and the channel set.

        The page is launched when `force` is *True* or the page is not opened yet.
        Normally this method will be called without any parameters.

        Parameters
        ----------
        channel : `str`, optional
            A different channel than the default (the default is set as *self.channel*).
        force : `bool`, optional
            If the browser page is forced to be opened (the default is *False*).
        verbose: `bool`, optional
            If True, print instructions if web browser is not opened (default *True*)

        Returns
        -------
        open_success : `bool`
            If True, the web browser open was successful.
        url : `str`
            The URL that is used in the user's web browser.
        """

        if not channel:
            channel = self.channel

        do_open = True if force else not self._is_page_connected()
        url = self.get_firefly_url(channel)
        open_success = False

        if do_open:
            open_success = webbrowser.open(url)
            if open_success is True:
                time.sleep(5)  # todo: find something better to do than sleeping
            else:
                if verbose is True:
                    self.display_url(url)

        return open_success, url

    @classmethod
    def get_instances(cls):
        """Get all current instances

        Returns
        -------
        `list`
            list of instances
        """
        return list(cls.instances)

    def upload_file(self, path):
        """
        Upload a file to the Firefly Server.

        Parameters
        ----------
        path : `str`
            Path of uploaded file. It can be fits, region, and various types of table files.

        Returns
        -------
        out: `str`
            Path of file after the upload.

        .. note:: 'pre_load' is not implemented in the server (will be removed later).
        """

        url = self.url_cmd_service + '?cmd=upload'
        files = {'file': open(path, 'rb')}
        result = self.session.post(url, files=files, headers=self.header_from_ws)
        if result.status_code == 200:
            index = result.text.find('$')
            return result.text[index:]
        raise requests.HTTPError('Upload unsuccessful')

    def upload_fits_data(self, stream):
        """
        Upload a FITS file like object to the Firefly server.
        The method should allow file like data to be streamed without using an actual file.

        Parameters
        ----------
        stream : `object`
            A FITS file like object containing fits data,
            such as if *f = open(<a_fits_path>)*, *f* is a file object.

        Returns
        -------
        out: `str`
            Path of file after the upload.
        """
        return self.upload_data(stream, 'FITS')

    def upload_text_data(self, stream):
        """
        Upload a text file like object to the Firefly server.
        The method should allow text file like data to be streamed without using an actual file.

        Parameters
        ----------
        stream : `object`
            A text file like object containing text data,
            such as if *f = open(<a_textfile_path>)*, *f* is a file object.

        Returns
        -------
        out: `str`
            Path of file after the upload.
        """
        return self.upload_data(stream, 'UNKNOWN')

    def upload_data(self, stream, data_type):
        """
        Upload a file like object to the Firefly server.
        The method should allow either FITS or non-FITS file like data to be streamed without using an actual file.

        Parameters
        ----------
        stream : `object`
            A file like object containing FITS data or others.
        data_type : {'FITS', 'UNKNOWN'}
            Data type, FITS or others.

        Returns
        -------
        out: `str`
            Path of file after the upload.
        """

        url = self.url_cmd_service + '?cmd=upload&preload='
        url += 'true&type=FITS' if data_type.upper() == 'FITS' else 'false&type=UNKNOWN'
        stream.seek(0, 0)
        data_pack = {'data': stream}
        result = self.session.post(url, files=data_pack, headers=self.header_from_ws)
        if result.status_code == 200:
            index = result.text.find('$')
            return result.text[index:]
        raise requests.HTTPError('Upload unsuccessful')

    @staticmethod
    def create_image_url(image_source):
        """
        Create image url or data uri according to the image source.

        Parameters
        ----------
        image_source : `str`
            An image path or image url.

        Returns
        -------
         out : `str`
            Data URI or image url.
        """
        return create_image_url(image_source)

    def dispatch(self, action_type, payload, override_channel=None):
        """
        Dispatch the action to the server by using 'POST' request.

        Parameters
        ----------
        action_type : `str`
            Action type, one of the actions from FireflyClient's attribute, `ACTION_DICT`.
        payload : `dict`
            Payload, the content varies based on the value of `action_type`.
        override_channel : `str`
            overrides the default channel

        Returns
        -------
        out : `dict`
            Status of the remote dispatch, like {'success': True}.
        """

        if payload is None:
            payload = {}
        if self.render_tree_id:
            payload['renderTreeId'] = self.render_tree_id
        channel = self.channel if override_channel is None else override_channel
        action = {'type': action_type, 'payload': payload}
        data = {'channelID': channel, 'cmd': 'pushAction', 'action': json.dumps(action)}
        debug('dispatch: type: %s, channel: %s \n%s' % (action_type, channel, dict_to_str(action)))

        return self._send_url_as_post(data)
    
    def get_payload_from_file(self, file_input):
        """Get payload for actions dispatched to Firefly server from the file input.

        It does all guesswork to determine file type and uploads it to the server if needed.

        Parameters
        ----------
        file_input : `str` or `file-like object`
            The input file to show. It can be a local file path, a URL to a
            remote file, name of a file on the server (return value of
            `upload_file()`), or a file-like object (such as an open IO stream).
        
        Returns
        -------
        out : `dict` 
            A dict that can be used as part of payload. The returned dict will 
            have one of the following keys:
            
            - 'fileOnServer': `str` (server file reference for the uploaded file/stream)
            - 'url': `str` (for a remote file)
        """
        if isinstance(file_input, str):
            if file_input.startswith('${'): # already a server file reference
                return {'fileOnServer': file_input}
            elif os.path.isfile(file_input): # local file path
                return {'fileOnServer': self.upload_file(file_input)}
            elif re.match(r'^https?://', file_input): # remote file url
                return {'url': file_input}
        elif isinstance(file_input, io.IOBase) and hasattr(file_input, 'seek'): # file-like object
            return {'fileOnServer': self.upload_data(file_input, 'UNKNOWN')}
        # invalid input
        raise ValueError('file_input must be a valid file path string or a file-like object')
    
    def get_title_from_file(self, file_input):
        """Get a title from a file input if possible."""
        if isinstance(file_input, str):
            if os.path.isfile(file_input):
                return os.path.basename(file_input)
            elif re.match(r'^https?://', file_input):
                url_basename = os.path.basename(file_input.split('?', 1)[0]) # remove query parameters
                _, ext = os.path.splitext(url_basename)
                return url_basename if ext else None
        return None

    # -------------------------
    # dispatch actions
    # -------------------------

    # --------------------------------------------------------------------------
    # action on adding cell for slate viewer,
    #           showing fits, tables, XYPlot, adding extension, and adding mask
    # -------------------------------------------------------------------------

    def change_triview_layout(self, layout):
        """
        Change the tri view layout

        Parameters
        ----------
        layout : `str`
            should be one of
            FireflyClient.TRIVIEW_ICov_Ch_T - top left: image/cov, top right: charts, bottom: tables
            FireflyClient.TRIVIEW_I_ChCov_T - top left: image, top right: charts/cov, bottom: tables
            FireflyClient.BIVIEW_ICov_Ch - left: image/cov, right: charts
            FireflyClient.BIVIEW_I_ChCov - left: image, right: charts/cov
            FireflyClient.BIVIEW_T_IChCov- left: tables, right: image/charts/cov
            FireflyClient.BIVIEW_IChCov_T- left: image/charts/cov, right: tables
        """

        if not self.is_triview():
            return {'success': True, 'warning': 'change_triview_layout ignored when not in triview mode'}
        if layout not in FireflyClient.tri_view_types_list:
            warning = '{} is an unknown layout type, valid types: {}'.format(layout, FireflyClient.tri_view_types_list)
            return {'success': False, 'warning': warning}

        self.dispatch(ACTION_DICT['TriviewLayout'], {'triviewLayout': layout})
        return {'success': True, 'description': FireflyClient.tri_view_layout_desc[layout]}

    def add_cell(self, row, col, width, height, element_type, cell_id=None):
        """
        Add a slate viewer cell.

        Parameters
        ----------
        row : `int`
            Cell row position.
        col : `int`
            Cell column position.
        width : `int`
            Cell horizontal size.
        height : `int`
            Cell vertical size.
        element_type : {'tables', 'images', 'xyPlots', 'tableImageMeta', 'coverageImage'}
            Cell element type. Use 'xyPlots' for histograms.
        cell_id : `str`, optional
            Cell Id.

        Returns
        -------
        out : `dict`
            Status of the request, like {'success': True, 'cell_id': 'Cell-1'}.
        """
        if not self.is_slate():
            return {'success': True, 'cell_id': cell_id if cell_id else 'noop',
                    'warning': 'add_cell ignored when not in slate mode'}

        # force the cell_id to be 'main' for table's case
        if element_type == LO_VIEW_DICT['table']:
            if not cell_id or cell_id != 'main':
                cell_id = 'main'
        else:
            if not cell_id:
                cell_id = gen_item_id('Cell')

        payload = {'row': row,
                   'col': col,
                   'width': width,
                   'height': height,
                   'type': element_type,
                   'cellId': cell_id}

        r = self.dispatch(ACTION_DICT['AddCell'], payload)
        r.update({'cell_id': cell_id})
        return r

    def reinit_viewer(self):
        """
        re-initialize the viewer

        Returns
        -------
         out : `dict`
            Status of the request, like {'success': True}.
        """
        return self.dispatch(ACTION_DICT['ReinitViewer'], {})

    def show_data(self, file_input, preview_metadata=False, title=None):
        """
        Show any data file of the type that Firefly supports:

        - Custom catalog or table in IPAC, CSV, TSV, VOTABLE, Parquet, or FITS table format
        - A ds9 region file
        - Images in FITS format, including multi-extension FITS files with images, tables, or a mixture of both
        - A Multi-Order Coverage Map (MOC) in FITS format
        - A Data Link Table file
        - A UWS job file
        
        Parameters
        ----------
        file_input : `str` or `file-like object`
            The input file to show. It can be a local file path, a URL to a
            remote file, name of a file on the server (return value of
            `upload_file()`), or a file-like object (such as an open IO stream).
        preview_metadata : `bool`, optional
            If True, preview the metadata of the file before loading the data.
            This allows you to select FITS extensions, table columns, etc. and 
            then you can click "Load" button in the UI to load your selections.
            Default is False.
        title : `str`, optional
            Title to display with the data view in the UI. If not provided,
            will be derived from the file name if possible.
        """
        payload = {
            **self.get_payload_from_file(file_input),
            'immediate': not preview_metadata,
            'displayName': self.get_title_from_file(file_input) if not title else title,
            # TODO: support optional keyword arguments like data_view_id, image/table/region options, etc.
            # **data_view_options
            }
        return self.dispatch(ACTION_DICT['ShowAnyData'], payload)

    def show_fits_image(self, file_input=None, file_on_server=None, url=None, 
                        plot_id=None, viewer_id=None, **additional_params):
        """
        Show a FITS image. 
        
        If the FITS file has multiple extensions/HDUs (for 
        images, tables, etc.), all the image extensions are displayed by default
        within the image plot. You can use the `multiImageIdx` parameter
        to display only a particular image extension from the file.

        Parameters
        ----------
        file_input : `str` or `file-like object`, optional
            The input file to show. It can be a local file path, a URL to a
            remote file, name of a file on the server (return value of
            `upload_file()`), or a file-like object (such as an open IO stream).
        file_on_server : `str`, optional
            The is the name of the file on the server.
            If you use `upload_file()`, then it is the return value of the method. Otherwise it is a file that
            Firefly has direct access to.

            .. deprecated:: 3.4.0
                Use `file_input` instead, which can automatically
                upload a local file and use its name on the server.
                If this parameter is passed, it will be ignored if
                `file_input` is also passed.
        url : `str`, optional
            URL of the FITS image file, if it's not a local file you can upload.

            .. deprecated:: 3.4.0 
                Use `file_input` instead, which can automatically
                infer if a URL is passed to it. If this parameter is passed,
                it will be ignored if `file_input` is also passed.
        plot_id : `str`, optional
            The ID you assign to the image plot. This is necessary to further control the plot.
        viewer_id : `str`, optional
            The ID you assign to the viewer (or cell) used to contain the image plot. If grid view is used for
            display, the viewer id is the cell id of the cell which contains the image plot.

            .. note:: Not needed in triview mode of Firefly, which is also 
                      the default view mode.

        **additional_params : optional keyword arguments
            Any valid fits viewer plotting parameter, please see the details in 
            `FITS plotting parameters`_ (note that they are case-insensitive).
            These also allow you to directly show an image retrieved from a 
            data service rather than from a file input, as explained in `this section`.

            .. _`FITS plotting parameters`:
                https://github.com/Caltech-IPAC/firefly/blob/dev/docs/fits-plotting-parameters.md
            .. _`this section`:
                https://github.com/Caltech-IPAC/firefly/blob/dev/docs/fits-plotting-parameters.md#parameters-for-specifying-fits-files-retrieved-from-a-service

            More options are shown as below:

            **multiImageIdx** : `int`, optional
                Display only a particular image extension from the file (zero-based index).
            **title** : `str`, optional
                Title to display with the image.

        Returns
        -------
        out : `dict`
            Status of the request, like {'success': True}.

        .. note:: `file_input` (previously `url` and `file_on_server`), and service specific `additional_params` are exclusively required.
            If more than one of these parameters are passed, precedence order is:
            service specific `additional_params` > `file_input` (> `file_on_server` > `url`).
        """
        # WebPlotRequest parameters
        wp_request = {'plotGroupId': 'groupFromPython',
                      'GroupLocked': False}
        payload = {'wpRequest': wp_request,
                   'useContextModifications': True}

        warning = None
        if not viewer_id or self.is_triview():
            warning = 'viewer_id is unnecessary and ignored in triview mode' if self.is_triview() and viewer_id else None
            viewer_id = FireflyClient.PINNED_IMAGE_VIEWER_ID

        payload.update({'viewerId': viewer_id})
        plot_id and payload['wpRequest'].update({'plotId': plot_id})

        # Handle different params of file input
        if file_on_server:
            warn('file_on_server is deprecated, use file_input parameter instead')
            payload['wpRequest'].update({'file': file_on_server})
        if url:
            warn('url is deprecated, use file_input parameter instead')
            payload['wpRequest'].update({'url': url})
        if file_input:
            file_payload = self.get_payload_from_file(file_input)
            if 'fileOnServer' in file_payload:
                # WebPlotRequest uses 'file' as the key for the file on server
                file_payload['file'] = file_payload.pop('fileOnServer')
            payload['wpRequest'].update(file_payload) # overrides url or file_on_server if any

        # Add the additional params including the image view related options, and
        # service specific options (which implicitly overrides the above file params if any, when WebPlotRequest is processed)
        additional_params and payload['wpRequest'].update(additional_params)

        r = self.dispatch(ACTION_DICT['ShowImage'], payload)
        warning and r.update({'warning': warning})
        return r
    
    def show_fits(self, *args, **kwargs):
        """
        .. deprecated:: 3.4.0
            Use show_fits_image() instead.
        """
        warn("show_fits() is deprecated. Use show_fits_image() instead.")
        return self.show_fits_image(*args, **kwargs)

    def show_fits_3color(self, three_color_params, plot_id=None, viewer_id=None):
        """
        Show a 3-color image constructed from the three color parameters

        Parameters
        ----------
        three_color_params : `list` of `dict` or `dict`
            A list or objects contains image viewer plotting parameters for either all bands or one single band.
            For valid image viewer plotting parameter, please see the details in `FITS plotting parameters`_ or
            the description of **additional_params** in function `show_fits_image`.

        plot_id : `str`, optional
            The ID you assign to the image plot. This is necessary to further control the plot.
        viewer_id : `str`, optional
            The ID you assign to the viewer (or cell) used to contain the image plot. If grid view is used for
            display, the viewer id is the cell id of the cell which contains the image plot.

        Returns
        -------
        out : `dict`
            Status of the request, like {'success': True}.
        """

        three_color = three_color_params if type(three_color_params).__name__ == 'list' else [three_color_params]
        for item in three_color:
            item.update({'GroupLocked': item.get('GroupLocked') if 'GroupLocked' in item else False})
            item.update({'plotGroupId': item.get('plotGroupId') if 'plotGroupId' in item else 'groupFromPython'})
            item.update({'Title': item.get('Title') if 'Title' in item else '3 Color'})
            if 'plotId' not in item and plot_id:
                item.update({'plotId': plot_id})

        payload = {'wpRequest': three_color, 'threeColor': True, 'useContextModifications': True}
        warning = None
        if not viewer_id or self.is_triview():
            warning = 'viewer_id unnecessary and ignored in triview mode' if self.is_triview() and viewer_id else None
            viewer_id = FireflyClient.PINNED_IMAGE_VIEWER_ID
        payload.update({'viewerId': viewer_id})

        r = self.dispatch(ACTION_DICT['ShowImage'], payload)
        warning and r.update({'warning': warning})
        return r

    def show_table(self, file_input=None, file_on_server=None, url=None, 
                   tbl_id=None, title=None, page_size=100, is_catalog=True,
                   meta=None, target_search_info=None, options=None, table_index=None,
                   column_spec=None, filters=None, visible=True):
        """
        Show a table.

        Parameters
        ----------
        file_input : `str` or `file-like object`, optional
            The input file to show. It can be a local file path, a URL to a
            remote file, name of a file on the server (return value of
            `upload_file()`), or a file-like object (such as an open IO stream).
        file_on_server : `str`, optional
            The name of the file on the server.
            If you use `upload_file()`, then it is the return value of the method. Otherwise it is a file that
            Firefly has direct access to.

            .. deprecated:: 3.4.0
                Use `file_input` instead, which can automatically
                upload a local file and use its name on the server.
                If this parameter is passed, it will be ignored if
                `file_input` is also passed.
        url : `str`, optional
            URL of the table file, if it's not a local file you can upload.

            .. deprecated:: 3.4.0 
                Use `file_input` instead, which can automatically
                infer if a URL is passed to it. If this parameter is passed,
                it will be ignored if `file_input` is also passed.
        tbl_id : `str`, optional
            A table ID. It will be created automatically if not specified.
        title : `str`, optional
            Title associated with the table.
        page_size : `int`, optional
            The number of rows that are shown in the table page (the default is 100).
        is_catalog : `bool`, optional
            If the table file is a catalog (the default is *True*) or not.
        meta : `dict`
            META_INFO for the table search request.
        target_search_info : `dict`, optional
            The information for target search, it may contain the following fields:

            - **catalogProject** : `str`
                Catalog project, such as *'WISE'*.
            - **catalog** : `str`
                Table to be searched, such as *'allwise_p3as_psd'*.
            - **use** : `str`
                Usage of the table search, such as *'catalog_overlay'*.
            - **position** : `str`
                Target position, such as *'10.68479;41.26906;EQ_J2000'*.
            - **SearchMethod** : {'Cone', 'Eliptical', 'Box', 'Polygon', 'Table', 'AllSky'}
                Target search method.
            - **radius** : `float`
                The radius for *'Cone'* or the semi-major axis for *'Eliptical'* search in terms of unit *arcsec*.
            - **posang** : `float`
                Position angle for *'Eliptical'* search in terms of unit *arcsec*.
            - **ratio** : `float`
                Axial ratio for *'Eliptical'* search.
            - **size** : `float`
                Side size for *'Box'* search in terms of unit *arcsec*.
            - **polygon** : `str`
                ra/dec of polygon corners, such as *'ra1, dec1, ra2, dec2,... raN, decN'*.
            - **filename** : `str`
                The name of file on server on multi-objects for *'Table'* search.

        options : `dict`, optional
            Containing parameters for table display, such as:

            - **removable** : `bool`
                if table is removable.
            - **showUnits** : `bool`
                if table shows units for the columns.
            - **showFilters** : `bool`
                if table shows filter button
        table_index : `int`, optional
            The table to be shown in case file input contains multiple tables. It is the extension number for
            a FITS file or the table index for a VOTable file. In unspecified, the server will fetch extension 1 from
            a FITS file or the table at index 0 from a VOTable file.
        column_spec : `str`, optional
            A string specifying column names from the table that will be shown. Column
            names must appear in the string in quotes, eg. '"ra","dec","mag"'
            It is possible to derive columns, e.g. '"flux"/"flux_err" as "SNR"'
        filters : `str`, optional
            A string specifying filters. Column names must be quoted.
            For example, '("coord_dec" > -0.478) and ("parent" > 0)'.
        visible: `bool`, optional
            If false, only load the table to Firefly but don't show it in the UI.
            Similar to `fetch_table()`

        Returns
        -------
        out : `dict`
            Status of the request, like {'success': True}.

        .. note:: `file_input` (previously `url` and `file_on_server`) and `target_search_info` are exclusively required.
            If more than one of these parameters are passed, precedence order is:
            `file_input` (> `file_on_server` > `url`) > `target_search_info`
        """
        has_file_input = bool(file_on_server) or bool(url) or bool(file_input)

        if not tbl_id:
            tbl_id = gen_item_id('Table')
        if not title:
            if has_file_input:
                title_from_file = self.get_title_from_file(file_input)
                title = title_from_file if title_from_file else tbl_id
            else:
                title = target_search_info.get('catalog', tbl_id)

        meta_info = {'title': title, 'tbl_id': tbl_id}
        meta and meta_info.update(meta)

        tbl_req = {'startIdx': 0, 'pageSize': page_size, 'tbl_id': tbl_id}
        if has_file_input:
            tbl_type = 'table' if not is_catalog else 'catalog'
            
            # Handle different params of file input
            source = None
            if file_input:
                file_payload = self.get_payload_from_file(file_input)
                source = file_payload.get('fileOnServer') or file_payload.get('url')
            elif file_on_server:
                warn('file_on_server is deprecated, use file_input parameter instead')
                source = file_on_server
            elif url:
                warn('url is deprecated, use file_input parameter instead')
                source = url

            tbl_req.update({'source': source, 'tblType': tbl_type,
                            'id': 'IpacTableFromSource'})
            table_index and tbl_req.update({'tbl_index': table_index})
        elif target_search_info:
            target_search_info.update(
                    {'use': target_search_info.get('use') if 'use' in target_search_info else 'catalog_overlay'})
            tbl_req.update({'id': 'GatorQuery', 'UserTargetWorldPt': target_search_info.get('position')})
            target_search_info.pop('position', None)
            tbl_req.update(target_search_info)
        else:
            raise ValueError('Either file_input/file_on_server/url or target_search_info parameter is required.')

        tbl_req.update({'META_INFO': meta_info})
        options and tbl_req.update({'options': options})
        column_spec and tbl_req.update({'inclCols': column_spec})
        filters and tbl_req.update({'filters': filters})

        payload = {'request': tbl_req}
        action_type = ACTION_DICT['ShowTable'] if visible else ACTION_DICT['FetchTable']

        return self.dispatch(action_type, payload)

    def fetch_table(self, file_on_server, tbl_id=None, title=None, page_size=1, table_index=None, meta=None):
        """
        Fetch table data without showing them

        Parameters
        ----------
        file_on_server : `str`
            The name of the file on the server.
            If you use `upload_file()`, then it is the return value of the method. Otherwise it is a file that
            Firefly has direct access to.
        tbl_id : `str`, optional
            A table ID. It will be created automatically if not specified.
        title : `str`, optional
            Title associated with the table.
        page_size : `int`, optional
            The number of rows to fetch.
        table_index : `int`, optional
            The table to be fetched in case `file_on_server` contains multiple tables. It is the extension number for
            a FITS file or the table index for a VOTable file. In unspecified, the server will fetch extension 1 from
            a FITS file or the table at index 0 from a VOTable file.
        meta : `dict`
            META_INFO for the table search request.

        Returns
        -------
        out : `dict`
            Status of the request, like {'success': True}.
        """
        if not tbl_id:
            tbl_id = gen_item_id('Table')
        if not title:
            title = tbl_id
        tbl_req = {'startIdx': 0, 'pageSize': page_size, 'source': file_on_server,
                   'id': 'IpacTableFromSource', 'tbl_id': tbl_id}
        if table_index:
            tbl_req.update({'tbl_index': table_index})

        meta_info = {'title': title, 'tbl_id': tbl_id}
        meta and meta_info.update(meta)
        tbl_req.update({'META_INFO': meta_info})
        payload = {'request': tbl_req, 'hlRowIdx': 0}
        return self.dispatch(ACTION_DICT['FetchTable'], payload)

    def show_xyplot(self, tbl_id, standalone=False, group_id=None, **chart_params):
        """
        Show a XY plot

        Parameters
        ----------
        tbl_id : `str`
            A table ID of the data to be plotted.
        standalone : `bool`, optional
            When it is *True*, the chart is always present in the chart area,
            no matter if the related table is present or not.
        group_id : `str`, optional
            Group ID of the chart group where the chart belongs to. If grid view is used, group id is
            the cell id of the cell which contains the chart.
        **chart_params : optional keyword arguments
            Parameters for XY Plot. The options are shown as below:

            **xCol**: `str`
                Column or expression to use for x values, can contain multiple column names,
                ex. *log(col)* or *(col1-col2)/col3*.
            **xError**: `str`
                Column or expression to use for x error, can contain multiple column names
            **yCol**: `str`
                Column or expression to use for y values, can contain multiple column names,
                ex. *sin(col)* or *(col1-col2)/col3*.
            **yError**: `str`
                Column or expression to use for x error, can contain multiple column names.
            **xyRatio** : `int` or  `float`
                Aspect ratio (must be between 1 and 10).
            **stretch** : {'fit', 'fill'}
                Stretch method.
            **plotStyle** : {'points', 'line', 'linepoints'}
                Style of XY plot.
            **chartTitle** : `str`
                Title of the chart.
            **xLabel** : `str`
                Label to use with x axis.
            **yLabel** : `str`
                Label to use with y axis.
            **xUnit** : `str`
                Unit for x axis.
            **yUnit** : `str`
                Unit for y axis.
            **xOptions** : `str`
                Comma separated list of x axis options: grid,flip,log.
            **yOptions** : `str`
                Comma separated list of y axis options: grid,flip,log.

        Returns
        -------
        out : `dict`
            Status of the request, like {'success': True}.

        .. note:: For the chart parameters, `xCol` and `yCol` are required, then all other
                  parameters are valid.
        """

        cid = gen_item_id('XYPlot')

        warning = None
        if self.is_triview():
            warning = 'group_id unnecessary and ignored in triview mode' if group_id else None
            group_id = FireflyClient.PINNED_CHART_VIEWER_ID
        elif not group_id:
            group_id = 'default' if standalone else tbl_id

        payload = {'chartId': cid, 'chartType': 'scatter',
                   'groupId': group_id, 'viewerId': group_id,
                   'params': {'tbl_id': tbl_id, **chart_params}}

        r = self.dispatch(ACTION_DICT['ShowXYPlot'], payload)
        warning and r.update({'warning': warning})
        return r

    def show_histogram(self, tbl_id, group_id=PINNED_CHART_VIEWER_ID, **histogram_params):
        """
        Show a histogram

        Parameters
        ----------
        tbl_id : `str`
            A table ID of the data to be plotted.
        group_id : `str`, optional
            Group ID of the chart group where the histogram belongs to. If grid view is used, group id is the
            cell id of the cell which contains the histogram.
        **histogram_params : optional keyword arguments
            Parameters for histogram. The options are shown as below:

            **col**: `str`
                Column or expression to use for x values, can contain multiple column names,
                ex. *log(col)* or *(col1-col2)/col3*.
            **xOptions**: `str`
                comma separated list of x axis options: flip,log.
            **yOptions**: `str`
                comma separated list of y axis options: flip,log.
            **falsePositiveRate**: `int` or `float`
                false positive rate for bayesian blocks algorithm.
            **numBins** : `int`
                Number of bins for fixed bins algorithm, default is 50.
            **binWidth** : `int` or `float`
                Bin width.

        Returns
        -------
        out : `dict`
            Status of the request, like {'success': True}.

        .. note:: For the histogram parameters, `col` is required.
        """

        warning = None
        if self.is_triview():
            warning = 'group_id unnecessary and ignored in triview mode' if group_id else None
            group_id = FireflyClient.PINNED_CHART_VIEWER_ID

        cid = gen_item_id('Histogram')
        payload = {'chartId': cid, 'chartType': 'histogram',
                   'groupId': group_id,
                   'viewerId': group_id,
                   'params': {'tbl_id': tbl_id, **histogram_params}}

        r = self.dispatch(ACTION_DICT['ShowXYPlot'], payload)
        warning and r.update({'warning': warning})
        return r

    def show_chart(self, group_id=PINNED_CHART_VIEWER_ID, **chart_params):
        """
        Show a plot.ly chart

        Plotly chart is described by a list of trace data and a layout. Any list in trace data can come from a table.

        For example, if a trace is defined by *{'tbl_id': 'wise', 'x': 'tables::w1pro', 'y': 'tables::w2mpro' }*,
        *x* and *y* points of the trace will come from *w1mpro* and *w2mpro* columns of the table with the id *wise*.

        See `plotly.js attribute reference <https://plot.ly/javascript/reference/>`_
        for the supported trace types and attributes. Note, that *data* and *layout* are expected to be
        basic Python object hierarchies, as *json.dumps* is used to convert them to JSON.

        Parameters
        ----------
        group_id : `str`, optional
            Group ID of the chart group where the chart belongs to. If grid view is used, group id is
            the cell id of the cell which contains the chart.
        **chart_params : optional keyword arguments
            Parameters for the chart. The options are shown as below:

            **chartId**: `str`, optional
                The chart ID.
            **data**: `list` of `dict`, optional
                A list of data for all traces of the plot.ly chart. Firefly-specific keys: *tbl_id*,
                *firefly* (for Firefly chart types).
            **layout**: `dict`, optional
                The layout for plot.ly layout. Optional *firefly* key refers to the information processed by Firefly.

        Returns
        -------
        out : `dict`
            Status of the request, like {'success': True}.

        """
        chart_id = chart_params.get('chartId') if 'chartId' in chart_params else gen_item_id('Plotly')
        warning = None
        if self.is_triview():
            warning = 'group_id unnecessary and ignored in triview mode' if group_id else None
            group_id = FireflyClient.PINNED_CHART_VIEWER_ID
        payload = {'chartId': chart_id,
                   'groupId': group_id,
                   'viewerId': group_id,
                   'chartType': 'plot.ly',
                   'closable': True}

        for item in ['data', 'layout']:
            (item in chart_params) and payload.update({item: chart_params.get(item)})

        r = self.dispatch(ACTION_DICT['ShowPlot'], payload)
        warning and r.update({'warning': warning})
        return r

    def show_coverage(self, viewer_id=None, table_group='main'):
        """
        Show image coverage associated with the active table in the specified table group

        Parameters
        ----------
        viewer_id : `str`, optional
            Viewer id, the cell id of the cell which contains the coverage image.
        table_group : `str`, optional
            Table group which the image coverage associated table belongs to.

        Returns
        -------
        out : `dict`
            Status of the request, like {'success': True}
        """
        if self.is_triview():
            return {'success': True, 'warning': 'show_coverage ignored in triview mode'}

        view_type = 'coverImage'
        cid = viewer_id if viewer_id else ("%s-%s" % (LO_VIEW_DICT[view_type], table_group))
        payload = {'viewerType': LO_VIEW_DICT[view_type], 'cellId': cid}
        return self.dispatch(ACTION_DICT['ShowCoverage'], payload)

    def show_image_metadata(self, viewer_id=None, table_group='main'):
        """
        Show the image associated with the active (image metadata) table in the specified table group

        Parameters
        ----------
        viewer_id : `str`, optional
            Viewer id, the cell id of the cell which contains the image from image metadata table.
        table_group : `str`, optional
            Table group which the image metadata table belongs to.

        Returns
        -------
        out : `dict`
            Status of the request, like {'success': True}
        """
        if self.is_triview():
            return {'success': True, 'warning': 'show_image_metadata ignored in triview mode'}

        view_type = 'imageMeta'
        cid = viewer_id if viewer_id else ("%s-%s" % (LO_VIEW_DICT[view_type], table_group))
        payload = {'viewerType': LO_VIEW_DICT[view_type], 'cellId': cid}

        return self.dispatch(ACTION_DICT['ShowImageMetaData'], payload)

    def add_extension(self, ext_type, plot_id=None, title='', tool_tip='',
                      shortcut_key='', extension_id=None, image_src=None):
        """
        Add an extension to the plot.
        Extensions are context menus that allows you to extend what Firefly can do when certain actions happen.

        Parameters
        ----------
        ext_type : {'AREA_SELECT', 'LINE_SELECT', 'POINT', 'table.select', 'table.highlight'}
            Extension type. It can be one of the values in the list or any Firefly action,
            or it will be reset to be 'NONE'.
        plot_id : `str`, optional
            Plot ID of the plot which the extension is added to, if not specified, this request
            is applied to all plots in the same group of the active plot.
        title : `str`, optional
            The title for the extension.
        tool_tip : `str`, optional
            Tooltip for the extension.
        extension_id : `str`, optional
            Extension ID. It will be created automatically if not specified.
        shortcut_key : `str`, optional
            use a letter for or a prefix it with 'meta' or 'ctrl' for example 'a', 'm', 'meta-m', 'ctrl-m'
        image_src : `str`, optional
            Image source of an icon to be displayed on the toolbar instead of the title.
            Image source could be an image path or an image url.

        Returns
        -------
        out : `dict`
            Status of the request, like {'success': True}.

        .. note:: If `image_src` is not specified, then no extension is added.
        """

        if not extension_id:
            extension_id = gen_item_id('Extension')
        payload = {'extension': {
                'id': extension_id, 'plotId': plot_id,
                'imageUrl': create_image_url(image_src) if image_src else None,
                'title': title, 'extType': ext_type,
                'toolTip': tool_tip, 'shortcutKey': shortcut_key}
             }
        return self.dispatch(ACTION_DICT['AddExtension'], payload)

    def table_highlight_callback(self, func, columns):
        """ Set a user-defined callback for table highlights

        Parameters
        ----------
        func : function
            The function to apply to the callback data. It must take as arguments:
            absolute_row, relative_row, column_data, table_id.
            absolute_row is a zero-based index to the highlighted row,
                in the original table data.
            relative_row is the index to the highlighted row in the table view.
            column_data is a dictionary of column name:data value pairs,
                for the highlighted row.
            table_id is a string identifying the table in Firefly.
        columns : `list` or None
            List of column names for which to return data.
            If the list is empty, the column_data will be an empty dictionary.
            If None, all columns are included.

        Returns
        -------
        func : the callback function that was added
        """
        def highlight_callback(event):
            if event['data'].get('type') == 'table.highlight':
                absolute_row = int(event['data']['row']['ROW_IDX'])
                relative_row = int(event['data']['row']['ROW_NUM'])
                tbl_id = event.get('tbl_id')
                col_data = copy(event['data']['row'])
                if columns is not None:
                    col_data.pop('ROW_IDX')
                    col_data.pop('ROW_NUM')
                    if len(columns) == 0:
                        for k in col_data:
                            col_data.pop(k)
                    else:
                        for k in columns:
                            col_data.pop(k)
                func(absolute_row, relative_row, col_data, tbl_id)
        self.add_listener(highlight_callback)
        self.add_extension(ext_type='table.highlight', extension_id='table_highlight')
        return highlight_callback

    def show_hips(self, plot_id=None, viewer_id=None, hips_root_url=None, hips_image_conversion=None,
                  **additional_params):
        """
        Show HiPS image.

        Parameters
        ----------
        plot_id : `str`, optional
            The ID you assign to the image plot. This is necessary to further control the plot.
        viewer_id : `str`, optional
            The ID you assign to the viewer (or cell) used to contain the image plot. If grid view is
            used for display, the viewer id is the cell id of the cell which contains the image plot.
        hips_root_url : `str`
            HiPS access URL
        hips_image_conversion: `dict`, optional
            The info used to convert between image and HiPS
        **additional_params : optional keyword arguments
            parameters for HiPS viewer plotting, the options are shown as below:

            **WorldPt** : `str`, optional
                World point as the center of the HiPS, if not defined, then get it from HiPS properties or
                set as the origin of the celestial coordinates.
            **Title** : `str`, optional
                Title to display with the HiPS.
            **SizeInDeg** : `int` or `float`, optional
                Field of view for HiPS.

        Returns
        -------
        out : `dict`
            Status of the request, like {'success': True}.
        """

        if not hips_root_url:
            return

        wp_request = {'plotGroupId': 'groupFromPython', 'hipsRootUrl': hips_root_url}
        additional_params and wp_request.update(additional_params)

        payload = {'wpRequest': wp_request}

        if not plot_id:
            plot_id = gen_item_id('Image')

        payload.update({'plotId': plot_id})
        wp_request.update({'plotId': plot_id})

        warning = None
        if not viewer_id or self.is_triview():
            warning = 'viewer_id unnecessary and ignored in triview mode' if self.is_triview() and viewer_id else None
            viewer_id = FireflyClient.PINNED_IMAGE_VIEWER_ID

        payload.update({'viewerId': viewer_id})

        if hips_image_conversion and type(hips_image_conversion) is dict:
            payload.update({'hipsImageConversion': hips_image_conversion})

        r = self.dispatch(ACTION_DICT['ShowHiPS'], payload)
        warning and r.update({'warning': warning})
        return r

    def show_image_or_hips(self, plot_id=None, viewer_id=None, image_request=None, hips_request=None,
                           fov_deg_fallover=0.12, allsky_request=None, plot_allsky_first=False):
        """
        Show a FiTS or HiPS image.

        Parameters
        ----------
        plot_id : `str`, optional
            The ID you assign to the image plot. This is necessary to further control the plot.
        viewer_id : `str`, optional
            The ID you assign to the viewer (or cell) used to contain the image plot. If grid view is
            used for display, the viewer id is the cell id of the cell which contains the image plot.
        image_request : `dict`, optional
            Request with fits plotting parameters. For valid fits viewer plotting parameter, please see the
            the description of `show_fits_image` or `show_fits_3color`.
        hips_request : `dict`, optional
            Request with hips plotting parameters. For valid HiPS viewer plotting parameter, please see the
            description of `show_hips`.
        fov_deg_fallover : `float`, optional
            The size in degrees that the image will switch between hips and a image cutout.
        allsky_request : `dict`, optional
             Allsky type request, like {'Type': 'ALL_SKY'}
        plot_allsky_first : `bool`, optional
             Plot all sky first If there is an all sky set up.
        Returns
        -------
        out : `dict`
            Status of the request, like {'success': True}.
        """

        if not image_request and not hips_request:
            return

        if not plot_id:
            plot_id = gen_item_id('Image')
        warning = None
        if not viewer_id or self.is_triview():
            warning = 'viewer_id unnecessary and ignored in triview mode' if self.is_triview() and viewer_id else None
            viewer_id = FireflyClient.PINNED_IMAGE_VIEWER_ID

        payload = {'fovDegFallOver': fov_deg_fallover, 'plotAllSkyFirst': plot_allsky_first,
                   'plotId': plot_id, 'viewerId': viewer_id}

        pg_key = 'plotGroupId'
        if not ((hips_request and hips_request.get(pg_key)) or (image_request and image_request.get(pg_key))):
            if hips_request:
                hips_request.update({pg_key: 'groupFromPython'})
            elif image_request:
                image_request.update({pg_key: 'groupFromPython'})

        image_request and payload.update({'imageRequest': image_request})
        hips_request and payload.update({'hipsRequest': hips_request})
        allsky_request and payload.update({'allSkyRequest': allsky_request})

        r = self.dispatch(ACTION_DICT['ShowImageOrHiPS'], payload)
        warning and r.update({'warning': warning})
        return r

    # ----------------------------
    # actions on image
    # ----------------------------

    def set_zoom(self, plot_id, factor=1.0):
        """
        Zoom the image.

        Parameters
        ----------
        plot_id : `str` or `list` of `str`
            ID of the plot to be zoomed. If `plot_id` is a list or tuple, then each plot in the list
            or the tuple is zoomed in order.
        factor : `int` or  `float`, optional
            Zoom factor for the image.

        Returns
        -------
        out : `dict`
            Status of the request, like {'success': True}.
        """

        def zoom_oneplot(one_plot_id, f):
            payload = {'plotId': one_plot_id, 'userZoomType': 'LEVEL', 'level': f, 'actionScope': 'SINGLE'}
            return self.dispatch(ACTION_DICT['ZoomImage'], payload)

        if isinstance(plot_id, tuple) or isinstance(plot_id, list):
            return [zoom_oneplot(x, factor) for x in plot_id]
        else:
            return zoom_oneplot(plot_id, factor)

    def set_pan(self, plot_id, x=None, y=None, coord='image'):
        """
        Relocate the image to center on the given image coordinate or EQ_J2000 coordinate.
        If no (x, y) is given, the image is re-centered at the center of the image.

        Parameters
        ----------
        plot_id : `str` or `list` of `str`
            ID of the plot to be panned. If plot_id is a list or tuple, then each plot in the list
            or the tuple is panned in order.
        x, y : `int` or  `float`, optional
            New center of x and y position to scroll to. Not required if coord is set 'image'
            because it will center on the image.
        coord : str, optional
            Coordinate system to use if x and y is specified like J2000, EQB2000, GAL, etc.
            The default is 'image' which will center on the image.

        Returns
        -------
        out : `dict`
            Status of the request, like {'success': True}.
        """

        payload = {'plotId': plot_id}
        if coord.startswith('image'):
            payload.update({'centerOnImage': 'true'})
        elif x and y:
            payload.update({'centerPt': f'{x};{y};{coord}'})

        return self.dispatch(ACTION_DICT['PanImage'], payload)
    
    def align_images(self, match_type='Standard', lock_match=False):
        """
        Align the images being displayed.

        Parameters
        ----------
        match_type : {'Standard', 'Target', 'Pixel', 'PixelCenter'}, optional
            Match type to use to align the images: align by WCS ('Standard'),
            by target ('Target'), by pixel prigins ('Pixel'), and by pixel at
            image centers ('PixelCenter').
        lock_match : bool, optional
            Whether to lock the alignment. Panning/zooming in one image will
            preserve the alignment in other images. Default is False.

        Returns
        -------
        out : `dict`
            Status of the request, like {'success': True}.
        
        """
        payload = dict(matchType=match_type, lockMatch=lock_match)
        return self.dispatch(ACTION_DICT['AlignImages'], payload)

    def set_stretch(self, plot_id, stype=None, algorithm=None, band=None, **additional_params):
        """
        Change the stretch of the image (no band or 3-color per-band cases).

        Parameters
        ----------
        plot_id : `str` or `list` of `str`
            ID of the plot to be stretched. If `plot_id` is a list or tuple, then each plot in the list
            or the tuple is stretched in order.
        stype : {'percent', 'minmax', 'absolute', 'zscale', 'sigma'}, optional
            Stretch method (the default is 'percent').
        algorithm : {'linear', 'log', 'loglog', 'equal', 'squared', 'sqrt', 'asinh', 'powerlaw_gamma'}, optional
            Stretch algorithm (the default is 'linear').
        band : {'RED', 'GREEN', 'BLUE', 'ALL'}, optional
            3-color band to apply stretch to
        **additional_params : optional keyword arguments
            Parameters for changing the stretch. The options are shown as below:

            **zscale_contrast** : `int`, optional
                zscale contrast (the default is 25).
            **zscale_samples** : `int`, optional
                zscale samples, int (the default is 600).
            **zscale_samples_perline** : `int`, optional
                zscale samples per line (the default is 120).

            **lower_value** : `int` or  `float`, optional
                Lower end of stretch (the default is 1).
            **upper_value** : `int` or  `float`, optional
                Upper end of stretch (the default is 90).

            **asinh_q_value** : `float`, optional
                The asinh softening parameter for Asinh stretch.
                Use Q=0 for linear stretch, increase Q to make brighter features visible.
                When not specified, Q is calculated by Firefly to use full color range.
            **gamma_value**
                The gamma value for Power Law Gamma stretch

        Returns
        -------
        out : `dict`
            Status of the request, like {'success': True}.

        .. note:: `zscale_contrast`, `zscale_samples`, and `zscale_samples_perline` are used when
                  `stype` is 'zscale', and `lower_value` and `upper_value` are used when `stype` is not 'zscale'.
        """

        serialized_rv = RangeValues.create_rv_by_stretch_type(algorithm, stype, **additional_params)
        bands_3color = ['RED', 'GREEN', 'BLUE', 'ALL']
        if not band:
            band_list = ['NO_BAND']
        elif band in bands_3color:
            band_list = ['RED', 'GREEN', 'BLUE'] if band == 'ALL' else [band]
        else:
            raise ValueError('invalid band: %s' % band)

        st_data = []
        for b in band_list:
            st_data.append({'band': b, 'rv': serialized_rv, 'bandVisible': True})

        payload = {'stretchData': st_data, 'plotId': plot_id}

        return_val = self.dispatch(ACTION_DICT['StretchImage'], payload)
        return_val['rv_string'] = serialized_rv
        return return_val

    def set_stretch_hprgb(self, plot_id, asinh_q_value=None, scaling_k=1.0,
                          pedestal_value=1, pedestal_type='percent'):
        """
        Change the stretch of RGB image (hue-preserving rgb case). When a parameter is a list,
        it must contain three elements, for red, green and blue bands respectively.
        Otherwise the parameter is a scalar that is used for all three bands.

        Parameters
        ----------
        plot_id : `str` or `list` of `str`
            ID of the plot to be stretched. If `plot_id` is a list or tuple, then each plot in the list
            or the tuple is stretched in order.
        asinh_q_value : `float`, optional
            The asinh softening parameter for Asinh stretch.
            Use Q=0 for linear stretch, increase Q to make brighter features visible.
            When not specified, Q is calculated by Firefly to use full color range for intensity.
        scaling_k : `float` or `list` of `float`, optional
            Scaling coefficient from 0.1 to 10 (the default is 1).
        pedestal_type : {'percent', 'minmax', 'absolute', 'zscale', 'sigma'} or `list` of `str`, optional
            Method to obtain pedestal value (the default is 'percent').
        pedestal_value : `float` or `list` of `float`, optional
            Minimum value (the default is 1 percent).

        Returns
        -------
        out : `dict`
            Status of the request, like {'success': True}.

        .. note:: `pedestal_value` is used when `pedestal_type` is not 'zscale'.
        """

        scaling_k = ensure3(scaling_k, 'scaling_k')
        pedestal_type = ensure3(pedestal_type, 'pedestal_type')
        pedestal_value = ensure3(pedestal_value, 'pedestal_value')

        st_data = []
        bands = ['RED', 'GREEN', 'BLUE']
        for i, band in enumerate(bands):
            serialized_rv = RangeValues.create_rv(stretch_type=pedestal_type[i],
                                                  lower_value=pedestal_value[i],
                                                  upper_value=99.0,
                                                  algorithm='asinh',
                                                  asinh_q_value=asinh_q_value,
                                                  rgb_preserve_hue=1,
                                                  scaling_k=scaling_k[i])
            st_data.append({'band': band, 'rv': serialized_rv, 'bandVisible': True})

        payload = {'stretchData': st_data, 'plotId': plot_id}
        return_val = self.dispatch(ACTION_DICT['StretchImage'], payload)
        return_val['rv_lst'] = [d['rv'] for d in st_data]
        return return_val

    def set_color(self, plot_id, colormap_id=0, bias=.5, contrast=1):
        """
        Change the color attributes (color map, bias, constrast) of an image plot.

        Parameters
        ----------
        plot_id : `str` or `list` of `str`
            ID of the image plot to be colored.
        colormap_id : `int`, optional
            ID of the colormap or color-table to use, ranging from 0 to 21.
            (the default is 0 i.e. grayscale). For HiPS image, -1 can be used
            to set the default hips image colors.
            Refer to the color dropdown on the image toolbar to see how IDs are mapped.
        bias : `float`, optional
            Bias to use, between 0 and 1 (the default is 0.5)
        contrast : `float`, optional
            Contrast to use, between 0 and 10 (the default is 1)

        Returns
        -------
        out : `dict`
            Status of the request, like {'success': True}.

        .. note:: when `colormap_id` is -1 for HiPS image, `contrast` and `bias` have no effect.
        """
        payload = {'plotId': plot_id,
                   'cbarId': colormap_id,
                   'bias': bias,
                   'contrast': contrast
                   }        
        return self.dispatch(ACTION_DICT['ColorImage'], payload)
    
    def set_rgb_colors(self, plot_id, use_red=True, use_green=True, use_blue=True,
                       bias=[.5,.5,.5], contrast=[1,1,1]):
        """
        Change the color attributes of a 3-color fits image plot.

        Parameters
        ----------
        plot_id : `str` or `list` of `str`
            ID of the image plot to be colored.
        use_red : `bool`, optional
            Whether to use red band in coloring the image (default is True)
        use_green : `bool`, optional
            Whether to use green band in coloring the image (default is True)
        use_blue : `bool`, optional
            Whether to use blue band in coloring the image (default is True)
        bias : `list` of `float`, optional
            Bias to use for each band, between 0 and 1 (the default is [0.5, 0.5, 0.5])
        contrast : `list` of `float`, optional
            Contrast to use for each band, between 0 and 10 (the default is [1, 1, 1])

        Returns
        -------
        out : `dict`
            Status of the request, like {'success': True}.
        """
        payload = {'plotId': plot_id, 
                   'useRed': use_red,
                   'useGreen': use_green,
                   'useBlue': use_blue,
                   'bias': bias,
                   'contrast': contrast
                   }
        return self.dispatch(ACTION_DICT['ColorImage'], payload)

    @staticmethod
    def parse_rvstring(rvstring):
        """parse a Firefly RangeValues string into a dictionary

        Parameters
        ----------
        rvstring : `str`
            RangeValues string as returned by the set_stretch method.

        Returns
        -------
        outdict : `dict`
            dictionary of the inputs
        """
        return RangeValues.parse_rvstring(rvstring)

    @staticmethod
    def rvstring_from_dict(rvdict):
        """create an rvstring from a dictionary

        Parameters
        ----------
        rvdict : `dict`
            Dictionary with the same keys as those returned by parse_rvstring

        Returns
        -------
        rvstring : `str`
            RangeValues string that can be passed to the show_fits_* methods
        """
        return RangeValues.rvstring_from_dict(rvdict)

    # -----------------------------------------------------------------
    # image line based footprint overlay
    # -----------------------------------------------------------------
    def overlay_footprints(self, footprint_file, footprint_image=None, title=None,
                           footprint_layer_id=None, plot_id=None, table_index=None, **additional_params):
        """
        Overlay a footprint dictionary on displayed images.
        The dictionary must be convertible to JSON format.

        Parameters
        ----------
        footprint_file : `str`
            footprint file with a table containing measurements and footprints
        footprint_image: `str`
            footprint image file
        title : `str`, optional
            Title of the footprint layer.
        footprint_layer_id : `str`, optional
            ID of the footprint layer to be created. It is automatically created if not specified.
        plot_id : `str` or `list` of `str`, optional
            ID of the plot that the footprint layer is created on.
            If None,  then overlay the footprint on all plots in the same group of the active plot.
        table_index : `int`, optional
            The table to be shown in case `file_on_server` contains multiple tables. It is the extension number for
            a FITS file or the table index for a VOTable file. In unspecified, the server will fetch extension 1 from
            a FITS file or the table at index 0 from a VOTable file.

        **additional_params : optional keyword arguments
            parameters for footprint overlays, the options are shown as below:

            **color** : `str`, optional
                color for the footprint. it is color name like 'red' or color code like 'rgb(0,0,0)'
            **style** : `str`, optional
                footprint display style, 'outline' or 'fill'
            **showText** : `bool`, optional
                show text, footprint id if there is, by the 'outline' display
            **selectColor** : 'str`, optional
                color for selected footprint
            **highlightColor** : `str` optional
                color for highlighted footprint

        Returns
        -------
        out : `dict`
            Status of the request, like {'success': True}.
        """

        if not footprint_layer_id:
            footprint_layer_id = gen_item_id('FootprintLayer')
        payload = {'drawLayerId': footprint_layer_id}

        title and payload.update({'title': title})
        plot_id and payload.update({'plotId': plot_id})
        footprint_file and payload.update({'footprintFile': footprint_file})
        footprint_image and payload.update({'footprintImageFile': footprint_image})
        table_index and payload.update({'tbl_index': table_index})
        additional_params and payload.update(additional_params)
        return self.dispatch(ACTION_DICT['ImagelineBasedFootprint'], payload)

    # -----------------------------------------------------------------
    # Region Stuff
    # -----------------------------------------------------------------

    def overlay_region_layer(self, file_on_server=None, region_data=None, title=None,
                             region_layer_id=None, plot_id=None):
        """
        Overlay a region layer on the loaded FITS images.
        The regions are defined either by a file or by text region description.

        Parameters
        ----------
        file_on_server : `str`, optional
            This is the name of the file on the server.  If you use `upload_file()`,
            then it is the return value of the method. Otherwise it
            is a file that Firefly has direct read access to.
        region_data : `str` or `list` of `str`, optional
            Region description, either a list of strings or a string.
        title : `str`, optional
            Title of the region layer.
        region_layer_id : `str`, optional
            ID of the region layer to be created. It is automatically created if not specified.
        plot_id : `str` or `list` of `str`, optional
            ID of the plot that the region layer is created on.
            If None,  then overlay region(s) on all plots in the same group of the active plot.

        Returns
        -------
        out : `dict`
            Status of the request, like {'success': True}.

        .. note:: `file_on_server` and `region_data` are exclusively required.
                  If both are specified, `file_on_server` takes the priority.
                  If none is specified, no region layer is created.
        """

        if not region_layer_id:
            region_layer_id = gen_item_id('RegionLayer')
        payload = {'drawLayerId': region_layer_id}

        title and payload.update({'layerTitle': title})
        plot_id and payload.update({'plotId': plot_id})
        if file_on_server:
            payload.update({'fileOnServer': file_on_server})
        elif region_data:
            payload.update({'regionAry': region_data})

        return self.dispatch(ACTION_DICT['CreateRegionLayer'], payload)

    def delete_region_layer(self, region_layer_id, plot_id=None):
        """
        Delete region layer from the loaded FITS images.

        Parameters
        ----------
        region_layer_id : `str`
            Region layer ID. The region layer with the region layer ID is to be removed.
        plot_id : `str` or a `list` of `str`, optional
            Plot ID. The region layer is removed from the plot with the plot ID.
            If not specified, then remove region layer from all plots in the same group of the active plot.

        Returns
        -------
         out : `dict`
            Status of the request, like {'success': True}.
        """

        payload = {'drawLayerId': region_layer_id}
        plot_id and payload.update({'plotId': plot_id})
        return self.dispatch(ACTION_DICT['DeleteRegionLayer'], payload)

    def add_region_data(self, region_data, region_layer_id, title=None, plot_id=None):
        """
        Add region entries to a region layer with the given ID.

        Parameters
        ----------
        region_data : `str` or `list` of `str`
            Region entries to be added.
        region_layer_id : `str`
            ID of region layer where the entries are added to.
        title : `str`, optional
            Title of the region layer. If the layer exists, the original title is replaced.
            If the layer doesn't exist, a new layer with the given title is created.
        plot_id : `str` or `list` of `str`, optional
            Plot ID. This is for the case that the region layer doesn't exist.
            If the region layer exists, this request applies to all plots attached to the layer.

        Returns
        -------
        out : `dict`
            Status of the request, like {'success': True}.

        .. note:: If no region layer with the given ID exists, a new region layer will be created
                  automatically just like how function `overlay_region_layer` works.

        """

        payload = {'regionChanges': region_data, 'drawLayerId': region_layer_id}
        plot_id and payload.update({'plotId': plot_id})
        title and payload.update({'layerTitle': title})
        return self.dispatch(ACTION_DICT['AddRegionData'], payload)

    def remove_region_data(self, region_data, region_layer_id):
        """
        Remove region entries from a region layer with the give ID.

        Parameters
        ----------
        region_data : `str` or `list` of `str`
            Region entries to be removed.
        region_layer_id : `str`
            ID of the region layer where the region entries are removed from.

        Returns
        --------
        out : `dict`
            Status of the request, like {'success': True}.
        """
        payload = {'regionChanges': region_data, 'drawLayerId': region_layer_id}

        return self.dispatch(ACTION_DICT['RemoveRegionData'], payload)

    def add_mask(self,  bit_number, image_number, plot_id, mask_id=None, color=None, title=None,
                 file_on_server=None):
        """
        Add a mask layer.

        Parameters
        ----------
        bit_number : `int`
            Bit number of the mask to overlay.
        image_number : `int`
            Image number of the mask layer HDU extension in FITS. This is a zero-based index.
        plot_id : `str`
            ID of the plot to overlay the mask on.
        mask_id : `str`, optional
            Mask ID. It will be created automatically if not specified.
        color : `str`, optional
            Color as an html color (eg. '#ff0000'(red), '#00ff00' (green)). A color will be
            created in default if not specified.
        title : `str`, optional
            Title of the mask layer.
        file_on_server : `str`, optional
            File to get the mask from. The mask will be taken from the original file if not specified.

        Returns
        --------
        out : `dict`
            Status of the request, like {'success': True}.
        """

        if not mask_id:
            mask_id = gen_item_id('MaskLayer')
        if not title:
            title = 'bit %23 ' + str(bit_number)

        payload = {'plotId': plot_id, 'imageOverlayId': mask_id, 'imageNumber': image_number,
                   'maskNumber': bit_number, 'maskValue': int(math.pow(2, bit_number)), 'title': title}
        color and payload.update({'color': color})
        file_on_server and payload.update({'fileKey': file_on_server})
        return self.dispatch(ACTION_DICT['PlotMask'], payload)

    def remove_mask(self, plot_id, mask_id):
        """
        Remove a mask layer from the plot with the given plot ID.

        Parameters
        ----------
        plot_id : `str`
            ID of the plot where the mask layer to be removed from.
        mask_id : `str`
            ID of the mask layer to be removed.

        Returns
        --------
        out : `dict`
            Status of the request, like {'success': True}
        """

        payload = {'plotId': plot_id, 'imageOverlayId': mask_id}
        return self.dispatch(ACTION_DICT['DeleteOverlayMask'], payload)

    # ----------------------------
    # actions on table
    # ----------------------------

    def apply_table_filters(self, tbl_id, filters):
        """
        Apply filters to a loaded table.

        Parameters
        ----------
        tbl_id : `str`
            ID of the table where you want to apply filters
        filters : `str`
            SQL WHERE clause-like string specifying filters. Column names must be quoted.
            For e.g. '("ra" > 185 AND "ra" < 185.1) OR ("dec" > 15 AND "dec" < 15.1) AND "band" IN (1,2)'.

        Returns
        --------
        out : `dict`
            Status of the request, like {'success': True}
        """
        tbl_req = {'tbl_id': tbl_id, 'filters': filters}
        payload = {'request': tbl_req}
        return self.dispatch(ACTION_DICT['TableFilter'], payload)
    
    def sort_table_column(self, tbl_id, column_name, sort_direction=''):
        """
        Sort a loaded table by a given column name.

        Parameters
        ----------
        tbl_id : `str`
            ID of the table where you want to apply sort
        column_name : `str`
            Name of the table column to sort
        sort_direction : {'', 'ASC', 'DESC'}, optional
            Direction of sort: '' for unsorted (or for removing the sort), 
            'ASC' for ascending, and 'DESC' for descending. Default is ''.

        Returns
        --------
        out : `dict`
            Status of the request, like {'success': True}
        """
        sort_directions = ['', 'ASC', 'DESC']
        if sort_direction not in sort_directions:
            raise ValueError(f'Invalid sort_direction. Valid values are {sort_directions}')
        
        tbl_req = {'tbl_id': tbl_id, 'sortInfo': f'{sort_direction},{column_name}'}
        payload = {'request': tbl_req}
        return self.dispatch(ACTION_DICT['TableSort'], payload)
