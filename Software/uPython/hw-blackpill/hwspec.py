# Hardware specific pin configuration for blackpill 
HW_SPEC = "HW BluePill Spec 0.1"

# --- Info ---
# PA11/12 are USB D-/+
# PA10 ID (optional)
# PA9 USB Sense (optional)
# -------------

# USART PA2/3

PIN_WIND = "PB14" 
PIN_SCL1 = "PB6"
PIN_SDA1 = "PB7"
PIN_SCL2 = "PB8"
PIN_SDA2 = "PB9"
PIN_NUM_LED1 = "PC13"

PINS_NUM_WATER = ("PB13", "PB12", "PB2", "PB10")

PIN_NUM_MOTOR1 = "PA7"   # hi=on
PIN_NUM_MOTOR1B = "PA5"   # hi=on
PIN_NUM_MOTOR1D = "PA6"  # hi=up
PIN_NUM_MOTOR2 = "PA4"   # hi=on
PIN_NUM_MOTOR2B = "PA2"   # hi=on
PIN_NUM_MOTOR2D = "PA3"  # hi=up

# Endswitches (UP,DOWN) - low active
PINS_NUM_END = (
    ("PB15","PA8"),    #1A
    ("PA11","PA12"),   #1B
    ("PA15","PB3"),    #2A
    ("PB4", "PB5")     #2B
)


DOSEN_NUM = ("PA1","PA0")

PIN_ADC_BATT = None # "PB0"
PINNUM_POWER = None # "PB1"   # needed for wakeup

PIN_BUTTON1 = "PA0"

UART_NUM = 1

    # VP
# pins PC14/15 are xtal32

# eof
