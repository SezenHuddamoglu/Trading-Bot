from flask import Blueprint, request, jsonify
import logging
from app.trading import get_trade_history, get_current_prices, start_trading
from app.trading_utils import start_trading_thread


api = Blueprint('api', __name__)

# Logger ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

target_coins = ["BNB", "BTC", "ETH", "DOGE", "SOL", "XRP"]

@api.route("/trades", methods=["GET"])
def get_trades():
    trades = get_trade_history()  
    logger.info(f"Trades data: {trades}")  
    return jsonify({"trades": trades})

@api.route("/coins", methods=["GET"])
def get_coins():
    prices = get_current_prices(target_coins)
    logger.info(f"Coins data: {prices}")  
    return jsonify({"coins": prices})

@api.route('/api/updateGraph', methods=['POST'])
def update_graph():
    # İstekten gelen parametreleri al
    data = request.get_json()

    # Ticaret parametrelerini çıkartın
    coin = data.get('coin')
    indicator = data.get('indicator')
    upper = data.get('upper')
    lower = data.get('lower')
    interval = data.get('interval')

    if not (coin and indicator and upper and lower and interval):
        return {"message": "Eksik parametreler"}, 400

    # Ticaret algoritmasını arka planda başlat
    start_trading_thread(coin, indicator, upper, lower, interval)

    return {"message": "Ticaret algoritması başlatıldı"}, 200
