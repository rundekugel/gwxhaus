# Hardware specific pin configuration for esp32lite
HW_SPEC = "HW esp32-lite Spec 0.2"


PIN_WIND = 13  
PIN_SCL1 = 5
PIN_SDA1 = 4
PIN_SCL2 = 2
PIN_SDA2 = 15
PIN_NUM_LED1 = 3  # on bigger boards it's pin2
PIN_BUTTON1 = None

PINS_NUM_WATER = (33,34,35,36)

PIN_NUM_MOTOR1 = 6   # hi=on
PIN_NUM_MOTOR2 = 8   # hi=on
PIN_NUM_MOTOR1B = None
PIN_NUM_MOTOR2B = None
# direction
PIN_NUM_MOTOR1D = 7  # hi=up
PIN_NUM_MOTOR2D = 9  # hi=up

# Endswitches (UP,DOWN) - low active
PINS_NUM_END = (
    (10,11),    #1A
    (10,11),    #1B
    (12,13),    #2A
    (12,13)     #2B
)

DOSEN_NUM = None # not used, too less pins

PIN_ADC_BATT = 14
PINNUM_POWER = 14   # needed for wakeup

UART_NUM = 2
#rx2/tx2 = 16/17

    # VP
# pins 32+33 are xtal32
# 22,21: scl/sda esp8266?
# esp32: scl/sda: 25/26 ; 18/19
