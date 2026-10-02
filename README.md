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

## Three-pin potentiometer (requires an MCP3008 ADC)

The Raspberry Pi GPIO header cannot measure the potentiometer's analog voltage directly. This example uses an **MCP3008** ADC and `pot_test.py`. The reed switch can stay on GPIO17; the connections below use different pins.

Power off the Pi before wiring. Use **3.3V, never 5V**, for the potentiometer and MCP3008.

| MCP3008 pin | Connect to Raspberry Pi |
| --- | --- |
| 16 VDD and 15 VREF | 3.3V, physical pin 1 |
| 14 AGND and 9 DGND | GND, physical pin 6 or another GND pin |
| 13 CLK | GPIO11 / SCLK, physical pin 23 |
| 12 DOUT | GPIO9 / MISO, physical pin 21 |
| 11 DIN | GPIO10 / MOSI, physical pin 19 |
| 10 CS/SHDN | GPIO8 / CE0, physical pin 24 |
| 1 CH0 | Potentiometer **middle** terminal |

Connect the potentiometer's two **outer** terminals to 3.3V and GND. Swapping the outer terminals reverses the direction of the reading. Identify MCP3008 pin 1 from the notch or dot on your specific chip; do not wire by its appearance in a photo alone.

Enable SPI on the Pi, then run the test:

```bash
sudo raspi-config
# Interface Options → SPI → Enable; reboot if prompted
sudo apt install python3-gpiozero python3-spidev
python3 pot_test.py
```

Turning the knob should change the printed position between approximately 0% and 100%. This wiring and code are specifically for an MCP3008 chip. If you have a different ADC module, use its pinout and driver instead.

## S3 device-window bridge

Keep the reed switch wired as above. On the Raspberry Pi, run:

```bash
python3 reed_bridge.py
```

Then open `https://sleep-airline-s3.vercel.app/?reed=1` in the browser **on the same Pi**. The S3 page must include the companion reed bridge change; the current published page does not yet have it. If the browser asks to access a device on the local network, allow this site to reach the bridge. Magnet close requests takeoff; magnet removal requests landing after takeoff completes. Browser audio may need one tap on the page before the first sensor event.

The companion S3 change is saved in `integration-patches/SleepAirlineS3-reed-bridge.patch`. A maintainer of `MorganHsuuu/SleepAirlineS3` can apply it from that repository's root with `git apply /path/to/SleepAirlineS3-reed-bridge.patch`, review it, and deploy the updated page.

The bridge serves only `127.0.0.1` and accepts cross-origin reads only from the S3 site. Do not expose port 8765 to the network.
