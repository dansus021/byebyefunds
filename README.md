# 💥 Crypto Liquidation Alert Bot

Real-time Binance & Bybit liquidation alerts with Telegram notifications. Categorizes liquidations as regular, whale, and mega whale — complete with emojis, tips, and auto-reconnect handling.

---

## ⚙️ Features

* 🔔 Real-time liquidation alerts from **Binance** and **Bybit**
* 🐋 Categorized by USD value: regular, whale, mega whale
* 💬 Sends formatted alerts to **Telegram channels**
* 🔄 Automatic reconnect on WebSocket disconnects
* 🛠️ Easy to deploy with `run.sh` and `systemd`

---

## 🚀 Setup Instructions

### 1. Clone & Enter Directory

```bash
git clone https://github.com/yourusername/liqalert.git
cd liqalert
```

### 2. Configure Environment

Edit `test.py` (rename to `liqfinal.py` if you want):

* Set your **Telegram bot token**
* Set your **channel ID** (e.g. `@yourchannel`)

### 3. Install Dependencies & Run

```bash
chmod +x run.sh
./run.sh
```

> This script will install dependencies and launch the bot.

---

## 🧩 Files

| File                      | Description                                    |
| ------------------------- | ---------------------------------------------- |
| `test.py` / `liqfinal.py` | Main bot script (Binance + Bybit alert engine) |
| `run.sh`                  | Installer and launcher shell script            |
| `requirements.txt`        | Python dependencies                            |
| `liquidation.service`     | Optional `systemd` service config              |

---

## 🛠️ systemd Autostart (Optional)

For VPS auto-run after reboot:

```bash
sudo cp liquidation.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable liquidation
sudo systemctl start liquidation
```

Check logs:

```bash
journalctl -u liquidation.service -f
```

---

## ✅ Telegram Example Output

```
🦈₿ [Bybit] #BTCUSDT

🗂️ Category: Mega Liquidation
📊 Side: 🔴 LONG 📈
💲 Price: $62,130.00
📏 Coin Size: 39.528
💰 Value: $2,457,000
⏰ Time: 2025-05-14 06:28:04
```

---

## 👷 Built With

* Python 3
* websocket-client
* python-telegram-bot
* schedule

---

## 📬 Feedback / Contribution

Open issues or PRs welcome!

---

## 📄 License

MIT
