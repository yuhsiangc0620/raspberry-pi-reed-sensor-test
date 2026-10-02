# Raspberry Pi reed sensor test

Simple test for a **two-wire, normally open reed switch**. The Raspberry Pi's internal pull-up keeps GPIO17 high while the switch is open; closing the switch to ground reports a detected magnet.

## Wiring

| Reed switch end | Raspberry Pi connection |
| --- | --- |
| Either end | BCM GPIO17, physical pin 11 |
| Other end | GND, physical pin 6 |

Do not connect the switch to 5V. If your sensor is a three-pin VCC/GND/DO module, check its voltage and output level before wiring it this way.

## Run on the Raspberry Pi

```bash
sudo apt update
sudo apt install python3-gpiozero
python3 reed_test.py
```

Move the magnet close to and away from the switch. The program prints `CLOSED - Magnet detected` or `OPEN - Magnet removed`, including the initial state. Press Ctrl+C to stop.
