# Hardware specific pin configuration for esp32lite
HW_SPEC = "HW esp32-lite Spec 0.3"

import esp32

PIN_WIND = 13  
PIN_SCL1 = 5
PIN_SDA1 = 4
PIN_SCL2 = 2
PIN_SDA2 = 15
PIN_NUM_LED1 = 22  # on bigger boards it's pin2
PIN_BUTTON1 = None

PINS_NUM_WATER = (27,33,32,18)

PIN_NUM_MOTOR1 = 25   # hi=on
PIN_NUM_MOTOR2 = 12   # hi=on
PIN_NUM_MOTOR1B = None
PIN_NUM_MOTOR2B = None
# direction
PIN_NUM_MOTOR1D = 26  # hi=up
PIN_NUM_MOTOR2D = 14  # hi=up

# Endswitches (UP,DOWN) - low active
PINS_NUM_END = (
    (34,23),    #1A
    (34,23),    #1B
    (35,19),    #2A
    (35,19)     #2B
)

DOSEN_NUM = None # not used, too less pins

PIN_ADC_BATT = 39
PINNUM_POWER = 36   # needed for wakeup

UART_NUM = 2
#rx2/tx2 = 16/17

    # VP
# pins 32+33 are xtal32
# 22,21: scl/sda esp8266?
# esp32: scl/sda: 25/26 ; 18/19
