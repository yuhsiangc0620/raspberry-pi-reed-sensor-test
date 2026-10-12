# Raspberry Pi reed sensor test

Raspberry Pi setup for two reed switches, an ADS1115 direction knob, and the Sleep Airline device kiosk. Older one-switch tests remain below for reference.

## 最新：單一裝置畫面與首次配網

`device_kiosk.py` 一次啟動本機設定頁、GPIO/ADC 橋接與 Chromium。未綁定時，樹莓派螢幕顯示離線可用的配對 QR 和暫時 Wi-Fi；手機掃 QR 後依 APP 指引加入該 Wi-Fi，並在**手機上的本機設定頁**輸入家中 Wi-Fi。綁定確認後，同一個 Chromium 畫面切到 S3 全螢幕飛機窗主頁，網址不再需要 `?device=1`，也不需要另開感測器測試分頁。

樹莓派先在可下載套件的網路環境完成安裝。需 Raspberry Pi OS 的 NetworkManager (`nmcli`)、Chromium、單一 `wlan0` Wi-Fi 介面，以及已開啟 I2C：

```bash
sudo apt update
sudo apt install network-manager chromium python3-gpiozero python3-smbus python3-qrcode i2c-tools
sudo raspi-config
# Interface Options → I2C → Enable
```

裝置端 PR 合併、Vercel 設定完配對環境變數並部署後，在**樹莓派桌面終端機**執行：

```bash
cd ~/raspberry-pi-reed-sensor-test
git pull
python3 device_kiosk.py
```

首次測試前，停止原本的 `device_bridge.py`、`reed_bridge.py` 及多餘 Chromium 感測器分頁，以免占用 GPIO 或連接埠。新的腳本會自行啟動 `device_bridge.py`。測試設定畫面可用 `python3 device_kiosk.py --dry-run`；不開瀏覽器可加 `--no-browser`。`--dry-run` 不會修改 Wi-Fi 或呼叫雲端，**不代表完成真正綁定**。

樹莓派在 `~/.config/sleep-airline/device.json` 儲存裝置 ID、憑證與已綁定的旅客 ID，檔案權限為 `0600`；請勿上傳 GitHub。家中 Wi-Fi 密碼只交給 NetworkManager，不寫入此檔案或 Vercel。解除綁定在手機 APP 操作；樹莓派收到後會回到 QR 畫面。若重開機時網路暫時無法連線，已綁定身分會保留。

更換家中 Wi-Fi 時，在手機 APP 個人設定選「更換家中 Wi-Fi」，於樹莓派原終端機按 Ctrl+C，然後執行 `python3 device_kiosk.py --reconfigure-wifi`。這會重新顯示熱點與 QR，但保留原旅客綁定；只有同一 Passenger ID 的有效授權可完成重配網。舊 Chromium 視窗請關閉，只留新 kiosk 畫面。

正式配網需實機驗證 `wlan0` 能以 NetworkManager 開熱點並切回家中 Wi-Fi，以及 iPhone Safari、Android Chrome 在切換 Wi-Fi 後能返回 APP。若熱點地址不是 `10.42.0.1`，需調整 `device_kiosk.py` 的 `HOTSPOT_IP` 與 APP 本機設定 URL。


## Standalone bridge test: two reeds + ADS1115 direction knob

Use `device_bridge.py` by itself when checking sensor wiring before launching the kiosk. The deployed S3 main page detects the bridge automatically.

| Input | Connection | Action |
| --- | --- | --- |
| Takeoff reed | BCM17 (pin 11) to GND | Magnet close starts takeoff |
| Landing reed | BCM27 (pin 13) to GND | Magnet close requests landing |
| Potentiometer | Middle pin to ADS1115 A0; outer pins to 3.3V and GND | Selects N, NE, E, SE, S, SW, W, NW before takeoff |
| ADS1115 | VDD to 3.3V (pin 1), GND and ADDR to GND, SDA to pin 3, SCL to pin 5 | I2C bus 1, address 0x48; ALRT unused |

Install dependencies and enable I2C with `sudo raspi-config` → Interface Options → I2C → Enable. Reboot if prompted, then confirm `i2cdetect -y 1` shows `48`.

```bash
sudo apt update
sudo apt install python3-gpiozero python3-smbus i2c-tools
```

Stop any running `reed_test.py` or `reed_bridge.py` with Ctrl+C, then:

```bash
git pull
python3 device_bridge.py
```

Keep the terminal running. Once the companion website PR is merged and deployed, open **https://sleep-airline-s3.vercel.app/ on the same Pi**. Allow local-device access and tap the page once for audio. Only use one device-control tab. Move both magnets away first; turn the knob, then approach the takeoff reed. Approaching the landing reed during takeoff queues landing until cruise. Moving away from either reed does not trigger a flight action.

The initial connection/reconnection never replays old reed commands. Both magnets active at once are ignored. The knob changes heading only while ready or landed (after the existing mood feedback completes), and does not fill in mood feedback. ADC errors retain the previous heading while reeds stay operational. The terminal and `http://127.0.0.1:8765/state` show readings for diagnosis.

For a reversed knob, run `python3 device_bridge.py --reverse`. Optional endpoint calibration: `--min-voltage 0.05 --max-voltage 3.25`. Default calibration is 0–3.3V. This script is also supplied in the S3 PR under `hardware/device_bridge.py` with detailed setup instructions.

The earlier single-reed and MCP3008 examples below are separate tests; they do not control this new three-input setup.

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

This is the older single-reed test: open `https://sleep-airline-s3.vercel.app/?reed=1` in the browser **on the same Pi** only when testing an older S3 deployment. The new kiosk uses two reed switches, ADS1115, and the main page without a query parameter. Browser audio may need one tap on the page before the first sensor event.

The companion S3 change is saved in `integration-patches/SleepAirlineS3-reed-bridge.patch`. A maintainer of `MorganHsuuu/SleepAirlineS3` can apply it from that repository's root with `git apply /path/to/SleepAirlineS3-reed-bridge.patch`, review it, and deploy the updated page.

The bridge serves only `127.0.0.1` and accepts cross-origin reads only from the S3 site. Do not expose port 8765 to the network.
