# Hardware specific pin configuration for blackpill 

PIN_WIND = "PA13"   # Pin(35, Pin.IN, pull=Pin.PULL_UP)    # pin35 is also ADC1_7
PIN_SCL1 = "PA5"
PIN_SDA1 = "PA4"
PIN_SCL2 = "PA2"
PIN_SDA2 = "PA15"
PIN_NUM_LED1 = "PA13"

PINS_NUM_WATER = ("PA4", "PA4", "PA4", "PA4")

PIN_NUM_MOTOR1 = "PA6"   # hi=on
PIN_NUM_MOTOR1D = "PA7"  # hi=up
PIN_NUM_MOTOR2 = "PA8"   # hi=on
PIN_NUM_MOTOR2D = "PA9"  # hi=up

# Endswitches (UP,DOWN) 
PINS_NUM_END = (
    ("PA10","PA11"),    #1A
    ("PA12","PA13"),    #1B
    ("PA14","PA15"),    #2A
    ("PA16","PA17")     #2B
)

DOSEN_NUM = ("PA18","PA18")

PIN_ADC_BATT = "PA14"
PINNUM_POWER = "PA14"   # needed for wakeup


    # VP
# pins 32+33 are xtal32
# 22,21: scl/sda esp8266?
# esp32: scl/sda: 25/26 ; 18/19
