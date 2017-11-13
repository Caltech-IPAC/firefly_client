
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
        with self.assertRaises(ConnectionError):
            firefly_client.FireflyClient('localhost:{}'.format(port))

