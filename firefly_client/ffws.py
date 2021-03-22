import os
import json
import time
from urllib.parse import urljoin
import math
import base64
import traceback
import _thread
from copy import deepcopy
try:
    from .env import Env
except ImportError:
    from env import Env

try:
    from .fc_utils import ALL, debug, warn, dict_to_str, DebugMarker
except ImportError:
    from fc_utils import ALL, debug, warn, dict_to_str, DebugMarker


MAX_CHANNELS = 3
def _make_key(channel, location): return channel+'---'+location


class FFWs:
    """
    For use only by FireflyClient to manage web sockets and channel connections. This class should never be instantiated
    directly. It should only be used though the static methods
    """

    connections = {}

    @classmethod
    def has(cls, channel, location): return _make_key(channel, location) in cls.connections

    @classmethod
    def get(cls, channel, location): return cls.connections.get(_make_key(channel, location))

    @classmethod
    def _open_ws_connection(cls, channel, wsproto, location, auth_headers, header_cb):
        key = _make_key(channel, location)
        if key not in cls.connections:
            if len(cls.connections) > MAX_CHANNELS:
                err_msg = 'You may only use %s channels for a python session' % MAX_CHANNELS
                raise ConnectionRefusedError(err_msg)
            cls.connections[key] = cls(channel, wsproto, location, auth_headers, header_cb)
            debug('starting chan: %s %s url:%s' % (channel, wsproto, location))
        return cls.connections[key]

    @classmethod
    def close_ws_connection(cls, channel, location):
        if cls.has(channel, location):
            cls.get(channel, location).disconnect()
            cls.connections.pop(_make_key(channel, location), None)

    @classmethod
    def add_listener(cls, wsproto, auth_headers, channel, location, callback, name=ALL, header_cb=None):
        cls._open_ws_connection(channel, wsproto, location, auth_headers, header_cb)
        cls.has(channel, location) and cls.get(channel, location).do_add_listener(callback, name)

    @classmethod
    def remove_listener(cls, channel, location, callback, name=ALL):
        if cls.has(channel, location):
            ffws = cls.get(channel, location)
            ffws.do_remove_listener(callback, name)
            if ffws.get_listener_cnt() == 0:
                ffws.disconnect()
                cls.connections.pop(_make_key(channel, location))

    @classmethod
    def wait_for_events(cls, channel, location):
        cls.has(channel, location) and cls.get(channel, location).do_run_forever()

    def __init__(self, channel, wsproto, location, auth_headers, header_cb):

        self.ws_url = urljoin('{}://{}/'.format(wsproto, location), 'sticky/firefly/events?channelID=%s' % channel)
        self.channel = channel
        self.location = location
        self.channel_headers = {'FF-channel': channel}
        self.listeners = {}
        self.forever_loop = True

        def on_message(wsapp, ev):
            try:
                self.received_message(ev, header_cb)
            except Exception as on_mess_ex:
                print(traceback.format_exc())
                raise on_mess_ex

        def on_open(wsapp):
            if not DebugMarker.firefly_client_debug:
                return
            try:
                debug('on open: Status: %d' % wsapp.sock.handshake_response.status)
                debug('response headers: \n%s' % dict_to_str(wsapp.sock.handshake_response.headers))
            except Exception as open_ex:
                print(traceback.format_exc())
                raise open_ex

        def on_error(wsapp, exception_from_socket):
            warn('Error: Websocket connection failed')
            print(exception_from_socket)
            warn('Websocket Status: %d' % wsapp.sock.handshake_response.status)
            warn('Websocket response headers: \n%s' % dict_to_str(wsapp.sock.handshake_response.headers))
            raise exception_from_socket

        def threaded_connect():
            try:
                import websocket
                socket_headers = self.channel_headers.copy()
                if auth_headers is not None:
                    socket_headers.update(auth_headers)
                self.websocket = websocket.WebSocketApp(url=self.ws_url, header=socket_headers, on_message=on_message,
                                                        on_open=on_open, on_error=on_error)
                self.debug_show_env(socket_headers)
                self.websocket.run_forever(ping_interval=10)
                self.forever_loop = False
                debug('websocket thread ended')
            except Exception:
                debug('websocket thread ended with exception')
                print(traceback.format_exc())

        try:
            _thread.start_new_thread(threaded_connect, ())
        except Exception as err:
            raise ValueError(Env.failed_net_message(location)) from err

    def debug_show_env(self, socket_headers):
        if not DebugMarker.firefly_client_debug:
            return
        debug('Attempting to connect\n    %s\n    %s\n    channel: %s' % (self.location, self.ws_url, self.channel))
        debug('Header sent to websocket connections: %s' % dict_to_str(socket_headers))

    def debug_header_event_message(self, ev):
        if not DebugMarker.firefly_client_debug:
            return
        debug('Event: %s' % ev['name'])
        log_ev = deepcopy(ev)
        try:
            log_ev['data']['plotState']['bandStateAry'] = '<<<<<truncated>>>>>'
        except KeyError:
            pass
        debug('JSON Data:\n%s' % json.dumps(log_ev, indent=2, default=str))
        debug('All Listeners for channel: %s, location: %s' % (self.channel, self.location))
        for callback, eventIDList in self.listeners.items():
            debug("          %s" % eventIDList)
        self.execute_callbacks(ev, do_callback=False)

    def execute_callbacks(self, ev, do_callback=True):
        name = ev['name']
        for callback, eventIDList in self.listeners.items():
            if name in eventIDList or ALL in eventIDList:
                callback(ev) if do_callback else debug('callback: %s' % name)

    def received_message(self, message, header_cb):
        try:
            ev = json.loads(message)
        except JSONDecodeError as err:
            warn('Error with JSON input - event string could not be parsed')
            warn(message)
            warn(err)
            return

        if ev['name'] == 'EVT_CONN_EST':
            try:
                conn_info = ev['data']
                debug('Connection established:\n    %s' % message)
                if self.channel is None:
                    self.channel = conn_info['channel']
                self.channel_headers = {'FF-channel': self.channel, 'FF-connID': conn_info.get('connID')}
                header_cb(self.channel_headers)
            except Exception as err:
                print(message)
                raise err
        else:
            self.debug_header_event_message(ev)
            self.execute_callbacks(ev)

    def disconnect(self):
        """Disconnect the WebSocket.
        """
        self.websocket.close()

    def do_add_listener(self, callback, name=ALL):
        debug('adding listener to %s, %s' % (self.channel, self.ws_url))
        if callback not in self.listeners.keys():
            self.listeners[callback] = []
        if name not in self.listeners[callback]:
            self.listeners[callback].append(name)

    def do_remove_listener(self, callback, name=ALL):
        debug('removing listener to %s, %s' % (self.channel, self.ws_url))
        if callback in self.listeners.keys():
            if name in self.listeners[callback]:
                self.listeners[callback].remove(name)
            if len(self.listeners[callback]) == 0:
                self.listeners.pop(callback)

    def get_listener_cnt(self):
        return len(self.listeners.keys())

    def do_run_forever(self):
        while self.forever_loop:
            time.sleep(10)
