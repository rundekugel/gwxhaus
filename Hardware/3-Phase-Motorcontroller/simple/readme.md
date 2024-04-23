# gwx-control
## Simple motor controller

Created to control a 3 phase motor to open/close windows of a greenhouse

Features:
- switch off motor, if window arrived at end position 
- stop for about 3 seconds, if direction changes to prevent too high current destroying power switches

Input: 
- motor on/off
- up/down
- switches for end positions

Output:
- +/- for optocoupler of power motor switcher. can control DC, AC 1 or 3 phase motors
- +/- for direction switch relais

