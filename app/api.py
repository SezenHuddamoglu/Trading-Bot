from flask import Flask, jsonify
import logging
from app.trading import get_trade_history, get_current_prices  # trading.py'den fonksiyonları import et

app = Flask(__name__)

# Logger ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

target_coins = ["BNB", "BTC", "ETH", "DOGE", "SOL", "XRP"]

@app.route("/trades", methods=["GET"])
def get_trades():
    """
    Get Trade History
    ---
    responses:
      200:
        description: Returns trade history from Binance
        schema:
          type: object
          properties:
            trades:
              type: array
              items:
                type: object
                properties:
                  symbol:
                    type: string
                  price:
                    type: string
                  time:
                    type: string
    """
    trades = get_trade_history()  # Binance'den alınan ticaret geçmişini al
    logger.info(f"Trades data: {trades}")  # Loglama
    return jsonify({"trades": trades})  # Ticaret geçmişini JSON olarak döndür

@app.route("/coins", methods=["GET"])
def get_coins():
    """
    Get Current Coin Prices
    ---
    responses:
      200:
        description: Returns current prices of target coins
        schema:
          type: object
          properties:
            coins:
              type: array
              items:
                type: object
                properties:
                  coin:
                    type: string
                  price:
                    type: string
    """
    prices = get_current_prices(target_coins)  # Binance'den alınan güncel fiyatları al
    logger.info(f"Coins data: {prices}")  # Loglama
    return jsonify({"coins": prices})  # Coin fiyatlarını JSON olarak döndür

