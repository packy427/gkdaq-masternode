import RPi.GPIO as GPIO
import time

# Define GPIO to LCD mapping
LCD_RS = 17
LCD_EN = 27
LCD_D4 = 25
LCD_D5 = 24
LCD_D6 = 23
LCD_D7 = 18

# Define some device constants
LCD_WIDTH = 20  # Maximum characters per line
LCD_CHR = True
LCD_CMD = False

LCD_LINE_1 = 0x80  # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0  # LCD RAM address for the 2nd line
LCD_LINE_3 = 0x94
LCD_LINE_4 = 0xD4

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005


def init():
    # Set up GPIO for LCD
    GPIO.setwarnings(True)
    GPIO.setmode(GPIO.BCM)  # Use BCM GPIO numbers
    GPIO.setup(LCD_EN, GPIO.OUT)  # EN
    GPIO.setup(LCD_RS, GPIO.OUT)  # RS
    GPIO.setup(LCD_D4, GPIO.OUT)  # DB4
    GPIO.setup(LCD_D5, GPIO.OUT)  # DB5
    GPIO.setup(LCD_D6, GPIO.OUT)  # DB6
    GPIO.setup(LCD_D7, GPIO.OUT)  # DB7
    
    # Initialise display
    write_byte(0x33, LCD_CMD)  # 110011 Initialise
    write_byte(0x32, LCD_CMD)  # 110010 Initialise
    write_byte(0x06, LCD_CMD)  # 000110 Cursor move direction
    write_byte(0x0C, LCD_CMD)  # 001100 Display On,Cursor Off, Blink Off
    write_byte(0x28, LCD_CMD)  # 101000 Data length, number of lines, font size
    write_byte(0x01, LCD_CMD)  # 000001 Clear display
    time.sleep(E_DELAY)


def set_cursor(col, row):
    """Move the cursor to an explicit column and row position."""
    if row == 0:
        write_byte((col + LCD_LINE_1), LCD_CMD)
    elif row == 1:
        write_byte((col + LCD_LINE_2), LCD_CMD)
    elif row == 2:
        write_byte((col + LCD_LINE_3), LCD_CMD)
    else:
        write_byte((col + LCD_LINE_4), LCD_CMD)


def clear():
    write_byte(0x01, LCD_CMD)
    time.sleep(0.003)   # Command takes a while


def write_byte(bits, mode):
    # Send byte to data pins
    # bits = data
    # mode = True  for character
    #        False for command

    GPIO.output(LCD_RS, mode)  # RS

    # High bits
    GPIO.output(LCD_D4, False)
    GPIO.output(LCD_D5, False)
    GPIO.output(LCD_D6, False)
    GPIO.output(LCD_D7, False)
    if bits & 0x10 == 0x10:
        GPIO.output(LCD_D4, True)
    if bits & 0x20 == 0x20:
        GPIO.output(LCD_D5, True)
    if bits & 0x40 == 0x40:
        GPIO.output(LCD_D6, True)
    if bits & 0x80 == 0x80:
        GPIO.output(LCD_D7, True)

    # Toggle 'Enable' pin
    toggle_enable()

    # Low bits
    GPIO.output(LCD_D4, False)
    GPIO.output(LCD_D5, False)
    GPIO.output(LCD_D6, False)
    GPIO.output(LCD_D7, False)
    if bits & 0x01 == 0x01:
        GPIO.output(LCD_D4, True)
    if bits & 0x02 == 0x02:
        GPIO.output(LCD_D5, True)
    if bits & 0x04 == 0x04:
        GPIO.output(LCD_D6, True)
    if bits & 0x08 == 0x08:
        GPIO.output(LCD_D7, True)

    # Toggle 'Enable' pin
    toggle_enable()


def toggle_enable():
    # Toggle enable
    time.sleep(E_DELAY)
    GPIO.output(LCD_EN, True)
    time.sleep(E_PULSE)
    GPIO.output(LCD_EN, False)
    time.sleep(E_DELAY)


def write_string(text):
    # Iterate through each character.
    for char in text:
        write_byte(ord(char), LCD_CHR)


def write_rpm(rpm):
    char = '*'      # Char to use as bar graph
    # Assumes 5k min 15k max with 20 spaces
    cols = int((rpm - 5000)/500)
    #prev_col = int((prev_rpm - 5000)/500)

    # Coerce to 20 col to prevent overruns
    cols = (min(cols, 20), 0)[0]
    #curr_col = (min(curr_col, 20), 0)[0]

    #delta = curr_col - prev_col
    #print("Delta: " + str(delta))
    set_cursor(0, 3)

    #if delta < 0:
     #   set_cursor(curr_col, 3)
     #   char = ' '

    # Only write changes to save some time
    for i in range(0, 20):
        if i <= cols:
            write_byte(ord('#'), LCD_CHR)
        else:
            write_byte(ord(' '), LCD_CHR)
