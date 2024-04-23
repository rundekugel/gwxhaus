# gwx-control-motor
## Simple motor controller

Created to control a 3 phase motor to open/close windows of a greenhouse
Created with Eagle Version 7.7

Features:
- switch off motor, if window arrived at end position 
- stop for about 3 seconds, if direction changes to prevent too high current destroying power switches

Input: 
- motor on/off
- up/down
- switches for end positions

Output:
- +/- for optocoupler of power motor switcher. Can control DC and AC, 1 to 3 phase motors.
- +/- for direction switch relais

