# Hardware specific pin configuration for esp8266
HW_SPEC = "HW esp8266 Spec 0.0"

# pinning for esp8266
PIN_WIND = 32
PIN_SCL1 = 5
PIN_SDA1 = 4
PIN_SCL2 = 18
PIN_SDA2 = 19
PIN_NUM_LED1 = 2

PINS_NUM_WATER = (27,33)

PIN_NUM_MOTOR1 = 25   # hi=on
PIN_NUM_MOTOR2 = 12   # hi=on
PIN_NUM_MOTOR1B = None
PIN_NUM_MOTOR2B = None
# direction
PIN_NUM_MOTOR1D = 26  # hi=up
PIN_NUM_MOTOR2D = 14  # hi=up

# Endswitches (UP,DOWN) - low active
PINS_NUM_END = (
    (None, None),    #1A
    (None, None),    #1B
    (None, None),    #2A
    (None, None)     #2B
)

DOSEN_NUM = (15,22)

PIN_ADC_BATT = 39
PINNUM_POWER = 36   # needed for wakeup

PIN_BUTTON1 = None

UART_NUM = 2

# eof



UART_NUM = 2
#rx2/tx2 = 16/17

# pins 32+33 are xtal32
