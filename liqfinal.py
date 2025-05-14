#!/usr/bin/env python
# Multi-Exchange Liquidation Alert Service

import json
import time
import logging
import threading
import websocket
import schedule
import requests
from datetime import datetime
from telegram import Bot
import random

# Configuration
TELEGRAM_BOT_TOKEN = "7924295389:AAE9jEGbOlaxYseZiOdM-OqjFhKrzZToxbI"
TELEGRAM_CHANNEL_ID = "@byebyefunds"

# Liquidation thresholds (in USD)
MINIMUM_AMOUNT_USD = 50000         # Regular liquidation
WHALE_THRESHOLD_USD = 250000       # Whale liquidation
MEGA_WHALE_THRESHOLD_USD = 1000000 # Mega whale liquidation

# WebSocket URLs
BINANCE_WS_URL = "wss://fstream.binance.com/stream?streams=!forceOrder@arr"
BYBIT_WSS_URL = "wss://stream.bybit.com/v5/public/linear"
BYBIT_REST_API = "https://api.bybit.com"

# Initialize Telegram bot
bot = Bot(token=TELEGRAM_BOT_TOKEN)

# Branding
CHANNEL_NAME = "Crypto Liquidation Alert"
BRAND_EMOJI = "⚡️"

# Logging configuration
LOG_FILE = "liquidation_alert.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# -------------------- Utilities --------------------

def send_telegram_message(message):
    try:
        footer = get_random_footer()
        branded = f"{message}\n\n{footer}\n{BRAND_EMOJI} {CHANNEL_NAME} | Powered by AI"
        bot.send_message(chat_id=TELEGRAM_CHANNEL_ID, text=branded, parse_mode="HTML")
        logger.info(f"✅ Sent to Telegram: {message[:50]}...")
    except Exception as e:
        logger.error(f"❌ Telegram send failed: {e}")


def get_random_footer():
    footers = [
         # — 1–21: Original & sebelumnya
        "💡 <i>Tip: Large liquidations often present counter-trend opportunities</i>",
        "🚀 <i>Stay tuned – real-time alpha delivered</i>",
        "📊 <i>Combine liquidations with order book data for edge</i>",
        "🔍 <i>Tip: Always cross-check funding rates before opening a position</i>",
        "🛡️ <i>Tip: Use stop-loss orders to protect against whip-saw moves</i>",
        "⚖️ <i>Did you know? Position sizing is key to surviving drawdowns</i>",
        "📈 <i>Fact: Binance handles over $50 billion in daily volume</i>",
        "🔗 <i>Fact: OKX was founded in 2017 and supports 400+ trading pairs</i>",
        "Ξ <i>Fact: Bybit’s perpetual futures have no expiry date</i>",
        "🎓 <i>Trivia: Bitcoin’s creator is known as Satoshi Nakamoto</i>",
        "🍕 <i>Trivia: First real-world BTC tx bought two pizzas in 2010</i>",
        "😅 <i>Joke: Why did the trader cross the road? To chase the liquidation!</i>",
        "😂 <i>Joke: My leverage jokes are margin-alized</i>",
        "🧠 <i>Pro Tip: Watch long–short ratio to gauge crowd sentiment</i>",
        "⚡ <i>Pro Tip: Fast feeds shave ms off your execution time</i>",
        "📐 <i>Pro Tip: Draw support/resistance—don’t trust indicators blindly</i>",
        "🔒 <i>Reminder: Never risk more than 1–2% of capital per trade</i>",
        "❗ <i>Reminder: High leverage amplifies gains AND losses</i>",
        "🌟 <i>Stay disciplined—consistency beats hero trades</i>",
        "🎯 <i>Focus on process, not outcomes; profits follow strategy</i>",

        # — 22–121: 100 tambahan
        # 1–10: Advanced Trading Tips
        "💡 <i>Monitor open interest alongside liquidations for trend strength</i>",
        "💡 <i>Use iceberg orders to hide your true size</i>",
        "💡 <i>Correlate BTC dominance with altcoin liquidations</i>",
        "💡 <i>Watch funding rate flips before anticipating squeezes</i>",
        "💡 <i>Use TWAP/VWAP in big liquidation zones</i>",
        "💡 <i>Hedge with options to soften liquidation impact</i>",
        "💡 <i>Scale into positions post-liquidation for better avg entry</i>",
        "💡 <i>Track whale wallets on-chain to foresee mega liquidations</i>",
        "💡 <i>Beware of fakeouts—confirm liquidation spikes with volume</i>",
        "💡 <i>Compare spot order book vs futures liquidation depth</i>",

        # 11–20: Risk Management
        "❗ <i>Check margin requirements before adding leverage</i>",
        "❗ <i>Liquidation prevention > chasing liquidations</i>",
        "❗ <i>Diversify across exchanges to manage counterparty risk</i>",
        "❗ <i>Keep collateral buffer for margin calls</i>",
        "❗ <i>Never go all-in—keep dry powder</i>",
        "❗ <i>Adjust leverage based on realized volatility</i>",
        "❗ <i>Use OCO orders for stop-loss & take-profit</i>",
        "❗ <i>Review risk-reward before high-leverage trades</i>",
        "❗ <i>Sync strategy with macro economic events</i>",
        "❗ <i>Rebalance portfolio after big liquidations</i>",

        # 21–30: Exchange & Chain Facts
        "📜 <i>Ethereum processed over 1M tx/day in 2024</i>",
        "📜 <i>Solana block times ~400 ms—fast but volatile</i>",
        "📜 <i>FTX collapse led to stricter margin rules</i>",
        "📜 <i>Uniswap V3 has concentrated liquidity pools</i>",
        "📜 <i>Binance Smart Chain is EVM-compatible</i>",
        "📜 <i>PoS ETH saves ~99% energy vs PoW</i>",
        "📜 <i>Layer-2 rollups cut gas fees up to 95%</i>",
        "📜 <i>Liquid staking pools increase leverage risk</i>",
        "📜 <i>Deribit ~60% share of BTC options market</i>",
        "📜 <i>Protocol collapses can spark cascade liquidations</i>",

        # 31–40: Market Psychology
        "🧠 <i>Fear & greed amplify liquidation clusters</i>",
        "🧠 <i>FOMO-driven leverage → massive liquidations</i>",
        "🧠 <i>Contrarian plays shine post-whale liquidations</i>",
        "🧠 <i>Regret aversion makes traders hold losers</i>",
        "🧠 <i>Anchoring bias skews perceived fair price</i>",
        "🧠 <i>Recency bias blinds to long-term trends</i>",
        "🧠 <i>Confirmation bias justifies dangerous leverage</i>",
        "🧠 <i>Journaling reveals emotional trading patterns</i>",
        "🧠 <i>Overconfidence peaks before big drawdowns</i>",
        "🧠 <i>Volume spikes often precede liquidation cascades</i>",

        # 41–50: Technical Indicators
        "📊 <i>RSI divergences warn of liquidation exhaustion</i>",
        "📊 <i>Bollinger squeezes often precede big moves</i>",
        "📊 <i>VWAP holds are strong post-liquidation levels</i>",
        "📊 <i>MACD zero-cross confirms momentum shifts</i>",
        "📊 <i>OBV tracks money flow around liquidations</i>",
        "📊 <i>Fibonacci helps plan post-liquidation entries</i>",
        "📊 <i>Ichimoku filters false breakouts</i>",
        "📊 <i>Limit indicators—focus on 2–3 core ones</i>",
        "📊 <i>Use multi-timeframe for liquidation zones</i>",
        "📊 <i>Heikin-Ashi smooths noise</i>",

        # 51–60: DeFi & On-Chain
        "⛓️ <i>Liquidation bots hunt undercollateralized loans</i>",
        "⛓️ <i>Keep collateral >150% on MakerDAO</i>",
        "⛓️ <i>Compound liquidates below maintenance threshold</i>",
        "⛓️ <i>Flash loans can trigger cascade liquidations</i>",
        "⛓️ <i>SushiSwap farming yields extra rewards</i>",
        "⛓️ <i>Watch protocol TVL for risk signals</i>",
        "⛓️ <i>On-chain alerts for margin calls</i>",
        "⛓️ <i>Yearn vaults auto-rebalance yields</i>",
        "⛓️ <i>Check oracle delays before trusting feeds</i>",
        "⛓️ <i>Curve locks liquidity for stability</i>",

        # 61–70: Security & Best Practices
        "🔒 <i>Enable 2FA on all exchanges</i>",
        "🔒 <i>Use hardware wallets for large holdings</i>",
        "🔒 <i>Rotate API keys every 30 days</i>",
        "🔒 <i>Whitelist withdrawal addresses</i>",
        "🔒 <i>Beware phishing links in Telegram</i>",
        "🔒 <i>Audit SSL certs on exchanges</i>",
        "🔒 <i>Audit smart contracts before big stakes</i>",
        "🔒 <i>Use read-only wallets for analytics</i>",
        "🔒 <i>Never share private keys</i>",
        "🔒 <i>Backup seed phrase offline</i>",

        # 71–80: Regulatory & Tax
        "📑 <i>Report gains per local tax laws</i>",
        "📑 <i>Keep logs for audits</i>",
        "📑 <i>SEC classifies some tokens as securities</i>",
        "📑 <i>Use self-hosted nodes to skip KYC caps</i>",
        "📑 <i>Check sanctions lists before txs</i>",
        "📑 <i>FATF Travel Rule applies to exchanges</i>",
        "📑 <i>Consult crypto accountant annually</i>",
        "📑 <i>Track stablecoin inflows for AML</i>",
        "📑 <i>MiCA standardizes EU rules in 2025</i>",
        "📑 <i>Archive blockchain receipts 7+ years</i>",

        # 81–90: Jokes & Memes
        "😜 <i>When in doubt, HODL—liquidation’s no joke!</i>",
        "😹 <i>Liquidations happen—just another day</i>",
        "🤣 <i>My alerts louder than ex’s texts</i>",
        "😂 <i>Margin call? More like margin fall!</i>",
        "😆 <i>Crypto winter’s coming—bring parka & stop-loss</i>",
        "😅 <i>Would tell a liquidation pun but it’s margin-alized</i>",
        "😝 <i>Don’t take life seriously—take profit first</i>",
        "😉 <i>My favorite candle avoids liquidation!</i>",
        "🙈 <i>Facing liquidation? Pretend you didn’t see it</i>",
        "😜 <i>Keep calm & check your margin level</i>",

        # 91–100: Motivation & Mindset
        "🌱 <i>Every liquidation is a lesson—learn & adapt</i>",
        "🌟 <i>Discipline today prevents regrets tomorrow</i>",
        "💪 <i>Strong risk mgmt builds unbreakable traders</i>",
        "🏆 <i>Consistency > luck in long-term success</i>",
        "🎯 <i>Set realistic goals—avoid margin overreach</i>",
        "🛤️ <i>Journey matters more than PnL</i>",
        "🚀 <i>Aim for process improvements, not just profits</i>",
        "🧭 <i>Stay course through choppy markets</i>",
        "📈 <i>Incremental gains compound into big wins</i>",
        "🎓 <i>Never stop learning—crypto evolves fast</i>",
    ]
    return random.choice(footers)


def get_coin_emoji(coin):
    mapping = {
        "BTC": "₿",     # Bitcoin
        "ETH": "Ξ",     # Ethereum
        "BNB": "🟡",    # Binance Coin
        "ADA": "A",     # Cardano
        "SOL": "◎",     # Solana
        "DOT": "●",     # Polkadot
        "XRP": "✕",     # Ripple
        "LTC": "Ł",     # Litecoin
        "DOGE": "Ð",    # Dogecoin
        "LINK": "🔗",   # Chainlink
        "MATIC": "⭑",  # Polygon
        "AVAX": "❄️",   # Avalanche
        "ATOM": "☢️",   # Cosmos
        "XLM": "★",     # Stellar
        "TRX": "Ｔ",    # TRON
        "NEO": "Ｎ",    # NEO
        "EOS": "Ｅ",    # EOS
        "FIL": "📁",    # Filecoin
        "AAVE": "🅰️",   # Aave
        "UNI": "🦄",    # Uniswap
        "CAKE": "🍰",   # PancakeSwap
        "SUSHI": "🍣",  # SushiSwap
        "FTT": "🛡️",   # FTX Token
        "XTZ": "✝️",    # Tezos
        "THETA": "🎥",  # Theta
        "VET": "✔️",    # VeChain
        "ALGO": "🔢",   # Algorand
        "ICP": "🌐",    # Internet Computer
        "EOS": "🌐",    # EOS (alternative)
        "KSM": "♛",     # Kusama
        "CHZ": "🎫",    # Chiliz
    }
    return f"{mapping.get(coin,'🪙')} "

# -------------------- Formatter --------------------

def format_liquidation_message(exchange, inner, category):
    """
    Format a liquidation message for Telegram, including exchange name.
    `inner` is the parsed JSON payload depending on exchange.
    """
    try:
        # Parse timestamp and details based on exchange
        if exchange == 'Binance':
            ts = datetime.fromtimestamp(int(inner.get("E", inner.get("o", {}).get("E", 0))) / 1000)
            symbol = inner.get("o", {}).get("s", "?")
            is_long = inner.get("o", {}).get("S") == "SELL"
            price = float(inner.get("o", {}).get("p", 0))
            qty = float(inner.get("o", {}).get("q", 0))
        elif exchange == 'Bybit':
            ts = datetime.fromtimestamp(int(inner.get("t", time.time())) / 1000)
            symbol = inner.get("symbol", "?")
            side = inner.get("side", "").lower()
            is_long = (side == "sell")
            price = float(inner.get("price", inner.get("p", 0)))
            qty = float(inner.get("size", inner.get("qty", 0)))
        else:
            return None

        usd = price * qty
        side_str = "🔴 LONG 📈" if is_long else "🔵 SHORT 📉"
        base = symbol.replace('USDT','').replace('USD','')
        coin_emoji = get_coin_emoji(base)

        # Category emoticon
        cat_emoji = {
            'regular': '🔔',
            'whale':   '🐋',
            'mega':    '🦈'
        }.get(category, '')

        return (
            f"{cat_emoji}{coin_emoji}<b>[{exchange}] #{symbol}</b>\n\n"
            f"🗂️ <b>Category:</b> {category.capitalize()} Liquidation\n"
            f"📊 <b>Side:</b> {side_str}\n"
            f"💲 <b>Price:</b> ${price:.2f}\n"
            f"📏 <b>Coin Size:</b> {qty:.3f}\n"
            f"💰 <b>Value:</b> ${usd:,.0f}\n"
            f"⏰ <b>Time:</b> {ts.strftime('%Y-%m-%d %H:%M:%S')}"
        )
    except Exception as e:
        logger.error(f"❌ Formatter err for {exchange}: {e}")
        return None

# -------------------- Binance Handler --------------------

def on_binance_message(ws, msg):
    try:
        payload = json.loads(msg)
        if payload.get("stream") and payload.get("data", {}).get("e") == "forceOrder":
            inner = payload["data"]
            price = float(inner.get("o", {}).get("p", 0))
            qty = float(inner.get("o", {}).get("q", 0))
            val = price * qty
            if val < MINIMUM_AMOUNT_USD:
                return
            if val < WHALE_THRESHOLD_USD:
                category = 'regular'
            elif val < MEGA_WHALE_THRESHOLD_USD:
                category = 'whale'
            else:
                category = 'mega'

            message = format_liquidation_message('Binance', inner, category)
            if message:
                send_telegram_message(message)
    except Exception as e:
        logger.error(f"❌ Binance msg err: {e}")

# -------------------- Bybit Monitor --------------------

class BybitLiquidationMonitor:
    def __init__(self):
        self.ws = None
        self.symbols = []

    def get_all_symbols(self):
        try:
            url = f"{BYBIT_REST_API}/v5/market/instruments-info?category=linear"
            res = requests.get(url).json()
            if res.get("retCode") == 0 and "list" in res.get("result", {}):
                return [item["symbol"] for item in res["result"]["list"] if item.get("status") == "Trading"]
        except Exception as e:
            logger.error(f"Error fetching Bybit symbols: {e}")
        # Fallback
        return ["BTCUSDT", "ETHUSDT", "SOLUSDT"]

    def start(self):
        self.symbols = self.get_all_symbols()
        if not self.symbols:
            logger.error("No symbols found. Aborting connection.")
            return

        batches = [self.symbols[i:i+50] for i in range(0, len(self.symbols), 50)]
        websocket.enableTrace(False)

        self.ws = websocket.WebSocketApp(
            BYBIT_WSS_URL,
            on_open=lambda ws: self.on_open(ws, batches),
            on_message=self.on_message,
            on_error=self._on_error,
            on_close=self._on_close,
            on_ping=lambda ws, msg: logger.debug("🏓 Sent ping"),
            on_pong=lambda ws, msg: logger.debug("🏓 Received pong")
        )

        self.thread = threading.Thread(
            target=lambda: self.ws.run_forever(ping_interval=20, ping_timeout=10),
            daemon=True
        )
        self.thread.start()
        logger.info("WebSocket thread started.")


    def on_open(self, ws, batches):
        for batch in batches:
            args = [f"liquidation.{sym}" for sym in batch]
            ws.send(json.dumps({"op": "subscribe", "args": args}))
            time.sleep(1)

    def on_message(self, ws, message):
        data = json.loads(message)
        if "topic" in data and "liquidation" in data["topic"] and "data" in data:
            items = data.get("data")
            if isinstance(items, dict):
                items = [items]
            for item in items:
                price = float(item.get("price", item.get("p", 0)))
                qty = float(item.get("size", item.get("qty", 0)))
                val = price * qty
                if val < MINIMUM_AMOUNT_USD:
                    continue
                if val < WHALE_THRESHOLD_USD:
                    category = 'regular'
                elif val < MEGA_WHALE_THRESHOLD_USD:
                    category = 'whale'
                else:
                    category = 'mega'
                message = format_liquidation_message('Bybit', item, category)
                if message:
                    send_telegram_message(message)
                    
    def _on_error(self, ws, error):
        logger.error(f"❌ Bybit WS err: {error} – reconnecting in 5s")
        time.sleep(5)
        self.start()

    def _on_close(self, ws, code, msg):
        logger.warning(f"⚠️ Bybit WS closed: {code} - {msg} – reconnecting in 5s")
        time.sleep(5)
        self.start()

# -------------------- Connection & Main --------------------

def connect_binance():
    ws = websocket.WebSocketApp(
        BINANCE_WS_URL,
        on_message=on_binance_message,
        on_error=lambda ws,e: logger.error(f"❌ Binance WS err: {e}"),
        on_close=lambda ws,code,msg: logger.warning(f"⚠️ Binance WS closed: {code} - {msg}")
    )
    threading.Thread(target=ws.run_forever, daemon=True).start()
    return ws

if __name__ == '__main__':
    logger.info("🚀 Starting Multi-Exchange Liquidation Alert Service")
    # Notify startup
    bot.send_message(
        chat_id=TELEGRAM_CHANNEL_ID,
        text=(
            f"🚀 <b>{BRAND_EMOJI} {CHANNEL_NAME} Live on Binance & Bybit!</b> 🚀\n"
            f"Started at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
        ),
        parse_mode="HTML"
    )

    # Launch watchers
    connect_binance()
    bybit_monitor = BybitLiquidationMonitor()
    bybit_monitor.start()

    # Keepalive and reconnect schedule
    schedule.every(6).hours.do(connect_binance)
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("⛔ Service stopped by user")
    finally:
        logger.info("⛔ Service shutdown complete")
