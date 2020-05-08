from __future__ import print_function
from future import standard_library
from urllib.parse import urljoin
from ws4py.client.threadedclient import WebSocketClient
from ws4py.client import HandshakeError
import json

ALL = 'ALL_EVENTS_ENABLED'
MAX_CHANNELS = 3
_connections = {}


def _get(channel):
    if channel in _connections:
        return _connections[channel]

    class Empty:
        headers = {'FF-channel': channel}
        def do_add_listener(self, channel, callback, name=ALL): return
        def do_remove_listener(self, channel, callback, name=ALL): return
        def do_run_forever(self): return
        def disconnect(self): return

    return Empty()


class FFWs(WebSocketClient):
    """
    For use only by FireflyClient to manage web sockets and channel connections. This class should never be instantiated
    directly. It should only be used though the static methods
    """

    @staticmethod
    def open_ws_connection(channel, wsproto, location):
        if channel not in _connections:
            if len(_connections) > MAX_CHANNELS:
                err_msg = 'You may only use %s channels for a python session' % MAX_CHANNELS
                raise ConnectionRefusedError(err_msg)
            _connections[channel] = FFWs(channel, wsproto, location)
        return _connections[channel]

    @staticmethod
    def close_ws_connection(channel):
        _get(channel).disconnect()
        _connections.pop(channel, None)

    @staticmethod
    def get_headers(channel): return _get(channel).headers

    @staticmethod
    def add_listener(channel, callback, name=ALL): _get(channel).do_add_listener(callback, name)

    @staticmethod
    def remove_listener(channel, callback, name=ALL): _get(channel).do_remove_listener(callback, name)

    @staticmethod
    def wait_for_events(channel): _get(channel).do_run_forever()

    def __init__(self, channel, wsproto, location):

        ws_url = urljoin('{}://{}/'.format(wsproto, location),
                         'sticky/firefly/events?channelID={}'.format(channel))
        WebSocketClient.__init__(self, ws_url)
        self.channel = channel
        self.conn_id = None
        self.headers = {'FF-channel': channel}
        self.listeners = {}

        try:
            self.connect()
        except (ConnectionRefusedError, HandshakeError) as err:
            err_message = ('Connection refused to URL {}\n'.format(url) +
                           'You may want to check the URL with your web browser.\n')
            if ('fireflyLabExtension' in os.environ) and ('fireflyURLLab' in os.environ):
                err_message += ('\nCheck the Firefly URL in ~/.jupyter/jupyter_notebook_config.py' +
                                ' or ~/.jupyter/jupyter_notebook_config.json')
            elif 'FIREFLY_URL' in os.environ:
                err_message += ('Check setting of FIREFLY_URL environment variable: {}'
                                .format(os.environ['FIREFLY_URL']))
            raise ValueError(err_message) from err

    def __handle_event(self, ev):
        for callback, eventIDList in self.listeners.items():
            if ev['name'] in eventIDList or ALL in eventIDList:
                callback(ev)

    def received_message(self, m):
        """Override the superclass's method
        """
        ev = json.loads(m.data.decode('utf8'))
        event_name = ev['name']

        if event_name == 'EVT_CONN_EST':
            try:
                conn_info = ev['data']
                if self.channel is None:
                    self.channel = conn_info['channel']
                if 'connID' in conn_info:
                    self.conn_id = conn_info['connID']

                self.headers = {'FF-channel': self.channel,
                                'FF-connID': self.conn_id}
            except:
                print('from callback exception: ')
                print(m)
        else:
            self.__handle_event(ev)

    def disconnect(self):
        """Disconnect the WebSocket.
        """
        self.close()

    def do_add_listener(self, callback, name=ALL):
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
        if callback not in self.listeners.keys():
            self.listeners[callback] = []
        if name not in self.listeners[callback]:
            self.listeners[callback].append(name)

    def do_remove_listener(self, callback, name=ALL):
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

        .. note:: `callback` in listener list is removed if all events are removed from the callback.
        """
        if callback in self.listeners.keys():
            if name in self.listeners[callback]:
                self.listeners[callback].remove(name)
            if len(self.listeners[callback]) == 0:
                self.listeners.pop(callback)

    def do_run_forever(self):
        WebSocketClient.run_forever(self)
