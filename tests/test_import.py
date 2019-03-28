
from __future__ import absolute_import, division, print_function

import socket
import unittest

import firefly_client


def get_unused_port():
    """Find an unused port on the local system

    Returns:
    --------
    port: `int`
       port number
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('localhost', 0))
    addr, port = s.getsockname()
    s.close()
    return port


class Test(unittest.TestCase):

    def test_connect(self):
        """A connection test on an unused socket"""
        port = get_unused_port()
        with self.assertRaises(ValueError):
            firefly_client.FireflyClient('http://localhost:{}/firefly'.format(port))

    def test_token_http(self):
        """A token cannot be used with a non-SSL url"""
        with self.assertRaises(ValueError):
            firefly_client.FireflyClient('http://127.0.0.1:8080/firefly',
                                         token='abcdefghij')
