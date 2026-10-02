"""Read a three-pin potentiometer through an MCP3008 ADC, channel 0."""

from time import sleep

from gpiozero import MCP3008


pot = MCP3008(channel=0)

print("Potentiometer test started. Turn the knob; press Ctrl+C to stop.")
try:
    while True:
        print(f"Position: {pot.value * 100:5.1f}%", flush=True)
        sleep(0.2)
except KeyboardInterrupt:
    pass
finally:
    pot.close()
