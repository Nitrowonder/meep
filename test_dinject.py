#Dependency Injection

from meep_example_app import MeepExampleApp
from meeplib import initialize
import unittest
import meeplib
import serve3
import socket

class fake_socket(object):
    closed = False
    def recv(self, size):
        return 'GET / HTTP/1.1\r\n\r\n'
    
    def sendall(self, data):
        assert data.startswith('HTTP')
        assert data.index('\r\n\r\n<html>')
    
    def getsockname(self):
    	return ('127.0.0.1','1234')
    
    def close(self):
        self.closed = True

class TestMeepLib(unittest.TestCase):
    
    def setUp(self):
        self.socket_save = socket.socket
        socket.socket = fake_socket()
        
    def test_for_message_existence(self):
    	fs = fake_socket()
        serve3.handle_connection(fs)
        assert fs.closed

    def tearDown(self):
        socket.socket = self.socket_save

if __name__ == '__main__':
    unittest.main()
