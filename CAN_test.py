import socket
import sys
import LCD_lib as LCD
import struct
import time

CAN_FORMAT = "<IB3x8s"      # Found it on the internet



def main():
    LCD.init()
    LCD.set_cursor(0, 0)
    LCD.write_string('Ran code')
    sock = socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
    interface = "can0"
    try:
        sock.bind((interface,))
    except OSError:
        LCD.set_cursor(0,0)
        LCD.write_string('No bueno')
        sys.stderr.write("Could not bind to interface '%s'\n" % interface)
        # do something about the error..
    while 1:
        can_id = 0xa1
        can_pkt = struct.pack(CAN_FORMAT, can_id, len(b"hello"), b"hello")

        sock.send(can_pkt)

        time.sleep(2)

        can_pkt = sock.recv(16)
        can_id, length, data = struct.unpack(CAN_FORMAT, can_pkt)
        data = data[:length]

        LCD.set_cursor(0, 0)
        LCD.write_string(str(can_id))
        LCD.set_cursor(0, 1)
        LCD.write_string(str(data))


if __name__ == '__main__':
    main()
