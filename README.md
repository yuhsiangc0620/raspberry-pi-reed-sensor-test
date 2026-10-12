# Sleep Airline 樹莓派裝置

此專案是實體裝置的正式執行程式：樹莓派負責兩個磁簧、ADS1115 旋鈕、首次 Wi-Fi 設定和全螢幕瀏覽器。飛機窗網頁與配對 API 由 [SleepAirlineS3](https://github.com/MorganHsuuu/SleepAirlineS3) 提供；手機 APP 由 [night-departures](https://github.com/yuhsiangc0620/night-departures) 提供。三者是一套裝置流程，沒有另外的感測器測試頁。

## 接線

接線前先關閉樹莓派電源。磁簧使用內建 pull-up，整套電路只使用 3.3V。

| 元件 | 連接 |
| --- | --- |
| 起飛磁簧 | BCM GPIO17（實體 Pin 11）與 GND |
| 降落磁簧 | BCM GPIO27（實體 Pin 13）與 GND |
| ADS1115 VDD / GND | 3.3V（Pin 1）／共用 GND |
| ADS1115 SDA / SCL | Pin 3／Pin 5 |
| ADS1115 ADDR / ALRT | ADDR 接 GND（位址 `0x48`）；ALRT 不接 |
| 可變電阻 | 兩側接 3.3V 和 GND；中間腳接 ADS1115 A0 |

## 安裝與啟動

先在樹莓派可上網時安裝套件並開啟 I2C：

```bash
sudo apt update
sudo apt install network-manager chromium python3-gpiozero python3-smbus python3-qrcode i2c-tools
sudo raspi-config
# Interface Options → I2C → Enable
```

重新啟動後，在樹莓派**桌面終端機**執行：

```bash
cd ~/raspberry-pi-reed-sensor-test
git pull
python3 device_kiosk.py
```

首次使用時，裝置螢幕顯示配對 QR 和暫時 Wi-Fi。用手機掃 QR，在 APP 建立或恢復 Passenger ID，依指示加入裝置 Wi-Fi，並在**手機上的裝置本機設定頁**輸入家中 Wi-Fi。裝置連網且伺服器確認綁定後，同一個 Chromium 視窗會開啟正式飛機窗。旋鈕選方位；磁鐵靠近 GPIO17 起飛，靠近 GPIO27 降落。移開磁鐵不觸發動作。

執行前先停止舊的 Python 橋接程式與多餘的 Chromium 感測器分頁，避免 GPIO 或連接埠 8765 被佔用。`device_kiosk.py` 會自行啟動 `device_bridge.py`；平常不需另外開啟它或加上 `?device=1`。

## 錯誤與維護

正式飛機窗會持續顯示橋接程式中斷或 ADS1115 讀取失敗的錯誤，恢復後自動清除。詳情也會印在樹莓派終端機。若 ADC 無法讀值，可執行 `i2cdetect -y 1`，確認 `48` 是否出現，並檢查 VDD、GND、SDA、SCL、ADDR 與旋鈕接線。若瀏覽器無法讀取本機橋接，確認已允許網站存取本機裝置。音效首次播放可能需要點一下畫面。

更換家中 Wi-Fi 時，先在手機 APP 個人設定選「更換家中 Wi-Fi」，在樹莓派終端機按 Ctrl+C，再執行：

```bash
python3 device_kiosk.py --reconfigure-wifi
```

原旅客綁定會保留；裝置重新顯示 QR 和熱點。解除綁定則在手機 APP 操作，樹莓派收到伺服器確認後回到 QR 畫面。

裝置 ID、憑證與旅客 ID 保存在 `~/.config/sleep-airline/device.json`，權限為 `0600`；家中 Wi-Fi 密碼交給 NetworkManager，不寫進此檔案或 Vercel。請勿把身分檔上傳 GitHub。

正式配網需要在 Raspberry Pi 上驗證 `wlan0` 能以 NetworkManager 切換熱點和家中 Wi-Fi，以及 iPhone Safari、Android Chrome 的切網返回流程。若熱點 IP 不是 `10.42.0.1`，須同步調整本程式與手機 APP 的本機設定網址。
