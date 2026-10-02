"""Test a two-wire reed switch on Raspberry Pi GPIO17."""

from signal import pause

from gpiozero import Button


# Wire one side of the switch to BCM GPIO17 (physical pin 11)
# and the other side to GND (physical pin 6).
reed = Button(17, pull_up=True, bounce_time=0.05)


def show_closed():
    print("CLOSED - Magnet detected", flush=True)


def show_open():
    print("OPEN - Magnet removed", flush=True)


reed.when_pressed = show_closed
reed.when_released = show_open

print("Reed sensor test started. Press Ctrl+C to stop.")
show_closed() if reed.is_pressed else show_open()
pause()
