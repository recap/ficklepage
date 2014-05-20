#!/usr/bin/python3

__author__ = 'reggie'


import socket
import sys

import hashlib
import base64
from hashlib import sha1
#from base64 import *
import http.server

import threading
from ficklepageindex import *

import queue

from queue import *


import atexit

HOST, PORT = '0.0.0.0', 9999
MAGIC = b"258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

connected = False

class FickleServer(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        #self.servers = PageIndex()

        pass

    def run(self):
        atexit.register(self.on_exit)

        listener = socket.socket()
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((HOST, int(PORT)))
        listener.listen(0)

        while 1:
            print("Waiting for a client to connect...")
            client, addr = listener.accept()
            threading.Thread(target=self.handler, args = (client, addr)).start()

        pass

    def handler(self, clientsock, addr):

        client = clientsock
        stream = client.makefile()

        # parse incoming data
        message = stream.readline().strip()
        while message:
            msg_list = message.split()
            if msg_list[0] == 'Sec-WebSocket-Key:':
                key = msg_list[1]
            elif msg_list[0] == '':
                pass
            #print(msg_list)
            message = stream.readline().strip()


        accept = self.get_hash(key)
        handshake = "HTTP/1.1 101 Switching Protocols\r\n"
        handshake += "Upgrade: websocket\r\n"
        handshake += "Connection: Upgrade\r\n"
        handshake += "Sec-WebSocket-Accept: " + accept + "\r\n"
        #handshake += "Sec-WebSocket-Protocol: chat, superchat\n"
        handshake += "\r\n"
        print(handshake)
        client.sendall(handshake.encode())

        id = self.read_data(client)
        print ("ID: "+id.decode('utf-8'))


        q = Queue()
        o = Queue()
        servers = PageIndex()
        servers.add_site(id.decode('utf-8'), (q, o))
        print ("Added server at: "+str(addr))
        connected = True

        #q.put("GET")
        while 1:
            msg = q.get()

            if msg == "GET":
                try:
                    self.send_data(client, msg)
                    message = self.read_data(client)
                    #print("Message: "+message.decode('utf-8'))
                    o.put(message.decode('utf-8'))

                except Exception:
                    print ("Disconnected site: "+id.decode('utf-8'))
                    connected = False
                    o.put("400")
                    break

                if not connected:
                     servers.remove_key(id.decode('utf-8'))
                     break



        # receiver = self.Receiver(client)
        # receiver.start()
        #
        # while True:
        #     #print("\033[94m", end="")
        #     message = input()
        #     if not connected:
        #         exit()
        #     try:
        #         self.send_data(client, message)
        #     except Exception:
        #         print("Can't send to client. The server will now quit.")
        #         exit()


    def on_exit(self):
        """Just change terminal colors back to normal."""
        #print("\033[0m", end = "")
        pass


    def get_hash(self, key):
        """
        Returns the correct hash value from the given key, ready to go, in the
        form of a string. The given key should also be a string.
        """
        accept = bytes(key, 'utf-8') + MAGIC

        accept = sha1(accept).digest()
        accept =  base64.encodebytes(accept)
        return accept.decode('utf-8').strip()


    def read_data(self, client):
        """
        Reads the client socket, getting data (in the form of raw bytes), by
        following the protocol. This handles the arbitrary sizing of WebSocket
        protocol headers, and reading the data using a masking key.
        Protocol (to my understanding):
        FRAME -> first 2 bytes
            byte 0: OPCODE: If the 7th bit is set, supposedly this is the last piece
                    of the payload. Not sure what this does at this point (ignored).
            byte 1: Indicates how long the length header is. If byte 1 == 126, the
                    length is 2 bytes long. If byte 1 == 127, the length is 8 bytes
                    long.
        LENGTH -> next 2 or 8 bytes (using byte 1 to differentiate)
            Translate the int of how long the data is (big endian bit order).
        MASK KEY -> next 4 bytes
            Use to decode the raw data sent by the client.
        DATA -> next n bytes (depending on LENGTH)
            Each byte should be XOR'd (bitwise exclusive or) with the MASK KEY byte,
            rotated mod 4 (i.e. first data byte is XOR'd with first MASK KEY,
            second w/ second, third w/ third, fourth w/ fourth, fifth w/ first again,
            and so on. This XOR'd data should be saved as the actual, readable,
            decoded data (as an array of bytes).
        """
        # get first 2 bytes (guaranteed to be header)
        frame = client.recv(2)

        # check if the 7th bit in the first byte is set:
        mask = 1 << 7
        first_set = (frame[0] & mask) == 0
        # ignored for now

        # second byte should ALWAYS have its 7th bit set
        # (frame[1] & mask) == 0 (should be true)

        # get data length from second byte
        data_len = frame[1] & 0x7F

        # data_len should be 126 or 127
        if data_len == 126:
            len_bytes = client.recv(2)
            # TODO - only works in python 3.2+
            data_len = int.from_bytes(len_bytes, byteorder='big')

        elif data_len == 127:
            len_bytes = client.recv(8)
            # TODO - only works in python 3.2+
            data_len = int.from_bytes(len_bytes, byteorder='big')

        #print('Got message: {} bytes long.'.format(data_len))

        # A masking key, used to read
        # Something to do with encryption I think - because it's not like anyone
        #   can just read the protocol, right?
        mask_key = client.recv(4)

        # receive the data using the determined data length
        received_bytes = client.recv(data_len)

        # construct the data byte array using the received bytes
        data = bytearray(data_len)
        for i, byte in enumerate(received_bytes):
            data[i] = byte ^ mask_key[i%4]

        return data


    def send_data(self, client, message):
        """Send a message to the WebSocket client."""
        data = bytearray()
        length = len(message)
        data.append(129) # data[0]
        if length <= 125:
            data.append(length) # data[1]

        else: # for now, can't handle more data
            return

        # append each character in message
        for c in message:
            data.append(ord(c))

        client.sendall(data)


    class Receiver(threading.Thread):
        """
        Receiver just reads data and prints it to the screen (so it doesn't block
        the user)
        """
        def __init__(self, client):
            threading.Thread.__init__(self)
            self.client = client;

        def run(self):
            global connected
            while True:
                try:
                    message = self.read_data(self.client)
                    #print("\r\033[93mClient: " + message.decode('utf-8') + "\033[94m")
                except Exception:
                    #print("\033[0mClient Disconnected. Type anything to quit.")
                    connected = False
                    break
            



# if __name__ == '__main__':
#     # register exit action (function)
#     atexit.register(on_exit)
#
#     listener = socket.socket()
#     listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#     listener.bind((HOST, int(PORT)))
#     listener.listen(0)
#
#     while 1:
#         print("Waiting for a client to connect...")
#         client, addr = listener.accept()
#         threading.threading.Thread(target=handler, args = (client, addr)).start()
