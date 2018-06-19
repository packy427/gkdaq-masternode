import socket
import sys
import struct
import time

CAN_FORMAT = "<IB3x8s"      # Found it on the internet


def init():
    sock = socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
    interface = "can0"
    try:
        sock.bind((interface,))
        return sock
    except OSError:
        sys.stderr.write("Could not bind to interface '%s'\n" % interface)
        # do something about the error..
        return None


def send_message(sock, can_id, dlc, data):
    can_pkt = struct.pack(CAN_FORMAT, can_id, dlc, data)
    sock.send(can_pkt)


def receive_message(sock):
    #print("<i> Entered receive function")
    can_pkt = sock.recv(16)
    #print("<i> Received from socket")
    can_id, dlc, data = struct.unpack(CAN_FORMAT, can_pkt)
    can_id &= 0x1FFFFFFF        # Mask off first 3 bits
    data = data[:dlc]
    return can_id, dlc, data
