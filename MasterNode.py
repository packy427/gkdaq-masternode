"""@package MasterNode"""
# -----------------------------------------------------------------------------
#   Filename   : MasterNode.py
#   Title      : Master Node Main
#   Author     : Patrick Kennedy (PK3)
#   Created    : 02/28/2018
#   Modified   : 02/28/2018
#   Version    : 0.1
#   Description:
#
# -----------------------------------------------------------------------------
#!/usr/bin/python

import time
from enum import Enum
import logging
import LCD_lib as LCD
import CAN_lib as CAN
import time
import socket
logging.basicConfig(level=logging.INFO)


# == GLOBAL VARIABLES == #
m_engine_temp = 0
m_exhaust_temp = 0
m_engine_speed = 0
m_kart_speed = 0
m_throttle_pos = 0
m_brake_pos = 0
m_steer_angle = 0
m_amb_temp = 0
m_accel_x = 0
m_accel_y = 0
m_accel_z = 0
m_gyro_x = 0
m_gyro_y = 0
m_gyro_z = 0
m_heading = 0
m_gps = 0
m_gps_lat = 0
m_gps_long = 0
m_humidity = 0
m_test_pot = 0

rx_can_id = 0
rx_can_dlc = 0
rx_can_data = 0

tx_can_id = 0
tx_can_dlc = 0
tx_can_data = 0

last_lap = time.time()
best_laptime = 500000000
laptime = 0
last_s1 = time.time()
s1_time = 0
last_s2 = time.time()
s2_time = 0
last_s3 = time.time()
s3_time = 0

can_socket = None


# == CAN IDS == #
class CANID(Enum):
    CAL_START        = 0x01
    CAL_CHANGEADDR   = 0x02
    CAL_CHANGEIO     = 0x03
    CAL_RESET        = 0x04
    CAL_EXIT         = 0x0F
    ENGINETEMP       = 0x10
    EXHAUSTTEMP      = 0x11
    ENGINESPEED      = 0x12
    GPS              = 0x20
    ACCELERATION     = 0x21
    HEADING          = 0x22
    AXLESPEED        = 0x23
    GYRATION         = 0x24
    THROTTLEPOSITION = 0x30
    BRAKEPOSITION    = 0x31
    STEERINGANGLE    = 0x32
    AMBIENTTEMP      = 0x40
    HUMIDITY         = 0x41
    TESTPOT          = 0x7F


def initialize():
    global can_socket
    # Initialize all functionality
    LCD.init()

    can_socket = socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
    interface = "can0"
    try:
        can_socket.bind((interface,))
    except OSError:
        LCD.set_cursor(0,0)
        LCD.write_string('CAN Init Error')

    # Write initial prompts
    LCD.set_cursor(0, 0)
    LCD.write_string("Acacia Racing GKDAQ")
    time.sleep(1)

    LCD.set_cursor(0, 3)
    for i in range(0, 20):
        LCD.write_byte(ord('='), LCD.LCD_CHR)
        time.sleep(0.1)

    time.sleep(2)
    LCD.clear()

    display_init()

# == MAIN LOOP == #
def main():
    initialize()

    while True:
        rx_can_id, rx_can_dlc, rx_can_data = CAN.receive_message(can_socket)
        decode_message(rx_can_id, rx_can_data)


# == SUPPORT FUNCTIONS == #
def decode_message(can_id, can_data):
    global last_s1
    global last_s2
    global last_s3
    global last_lap
    global best_laptime


    # Test Potentiometer
    if can_id == CANID.TESTPOT:
        m_test_pot = from_byte_array(can_data, 2)
        print("<i> Test Pot: " + str(m_test_pot))
    # Engine head temperature
    elif can_id == 16:
        m_engine_temp = from_byte_array(can_data, 2)
        update_temp(0, int(m_engine_temp))
        print("<M> Eng Temp: " + str((int(m_engine_temp))))
    # Exhaust gas temperature
    elif can_id == 17:
        m_exhaust_temp = from_byte_array(can_data, 2)
        update_temp(1, int(m_exhaust_temp));
        print("<M> Exh Temp: " + str(int(m_exhaust_temp)));
    # Engine speed
    elif can_id == 18:
        m_engine_speed = from_byte_array(can_data, 2)
        update_rpm((int(m_engine_speed)))
        print("<M> Eng Speed: " + str(int(m_engine_speed)));
    # GPS
    elif can_id == 32:
        m_gps = from_byte_array(can_data, 8)
        m_gps_lat = from_byte_array(can_data, 8) & 0xFFFFFFFF
        m_gps_long = from_byte_array(can_data, 8) >> 32
        print("<M> GPS Lati: " + str(m_gps_lat))
        print("<M> GPS Long: " + str(m_gps_long))
        print(m_gps)
        if m_gps_lat == 404173:
            s1_time = time.time() - last_s3
            last_s1 = time.time()
            update_split(1, round(s1_time, 1))
        elif m_gps_lat == 404170:
            s2_time = time.time() - last_s1
            last_s2 = time.time()
            update_split(2, round(s2_time, 1))
        elif m_gps_lat == 404167:
            s3_time = time.time() - last_s2
            last_s3 = time.time()
            update_split(3, round(s3_time, 1))
            laptime = time.time() - last_lap
            last_lap = time.time()
            if laptime < best_laptime:
                update_lap(1, round(laptime, 1))
                best_laptime = laptime
            update_lap(0, round(laptime, 1))

    # Acceleration
    elif can_id == CANID.ACCELERATION:
        m_accel_x = can_data
        m_accel_y = can_data
        m_accel_z = can_data
        print("<i> Rcv test_pot: " + str(m_accel_z));
    # Heading
    elif can_id == CANID.HEADING:
        m_heading = can_data
        print("<i> Rcv heading: " + str(m_heading));
    # Axle speed
    elif can_id == CANID.AXLESPEED:
        m_kart_speed = can_data
        print("<i> Rcv kart_speed: " + str(m_kart_speed));
    # Gyration
    elif can_id == CANID.GYRATION:
        m_gyro_x = can_data
        m_gyro_y = can_data
        m_gyro_z = can_data
        print("<i> Rcv test_pot: " + str(m_gyro_x));
    # Throttle position
    elif can_id == CANID.THROTTLEPOSITION:
        m_throttle_pos = can_data
        print("<i> Rcv throttle_pos: " + str(m_throttle_pos));
    # Brake position
    elif can_id == CANID.BRAKEPOSITION:
        m_brake_pos = can_data
        print("<i> Rcv brake_pos: " + str(m_brake_pos));
    # Steering angle
    elif can_id == CANID.STEERINGANGLE:
        m_steer_angle = can_data
        print("<i> Rcv steer_angle: " + str(m_steer_angle));
    # Ambient temperature
    elif can_id == CANID.AMBIENTTEMP:
        m_amb_temp = can_data
        print("<i> Rcv amb_temp: " + str(m_amb_temp));
    # Humidity
    elif can_id == CANID.HUMIDITY:
        m_amb_humidity = can_data
        print("<i> Rcv amb_humidity: " + str(m_amb_humidity));
    else:
        print("<x> No matching CAN ID")


def from_byte_array(array, length):
    data = 0
    for i in range(0, length):
        data += (array[i] << (8 * i))
    return data

def display_init():
    # Row 0
    LCD.set_cursor(0,0)
    LCD.write_string('Last:')
    LCD.set_cursor(11,0)
    LCD.write_string('Best:')
    # Row 1
    LCD.set_cursor(0,1)
    LCD.write_string('(    )-(    )-(    )')

    # Row 2
    LCD.set_cursor(0, 2)
    LCD.write_string('EHT:')
    LCD.set_cursor(11, 2)
    LCD.write_string('EGT:')
    # Row 3 is RPM

def update_split(split_num, split_time):
    if split_num == 3:
        col = 15
    elif split_num == 2:
        col = 8
    else:
        col = 1
    out_str = str(split_time)
    LCD.set_cursor(col, 1)
    padding = 4 - len(out_str)
    for i in range(0, padding):
        LCD.write_string(" ")
    LCD.write_string(out_str[0:4])

def update_lap(best_lap, lap_time):
    if best_lap != 0:
        col = 16
    else:
        col = 5
    out_str = str(lap_time)
    LCD.set_cursor(col, 0)
    padding = 4 - len(out_str)
    for i in range(0, padding):
        LCD.write_string(" ")
    LCD.write_string(out_str[0:4])

def update_temp(egt, temp):
    if egt != 0:
        col = 15
    else:
        col = 4
    out_str = str(temp)
    LCD.set_cursor(col, 2)
    padding = 4 - len(out_str)
    for i in range(0, padding):
        LCD.write_string(" ")

    LCD.write_string(out_str[0:4])

def update_rpm(rpm):
    LCD.write_rpm(rpm)
    
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        print("Bye bye")

