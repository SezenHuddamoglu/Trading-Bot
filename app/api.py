from flask import Blueprint, request, jsonify
import logging
from app.trading import start_trading, reset_trades

api = Blueprint('api', __name__)

# Logger ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

@api.route("/trades", methods=["GET"])
def get_trades():
    from app.trading import get_trade_history
    trades = get_trade_history()
    logger.info(f"Trades data: {trades}")
    return jsonify({"trades": trades})

@api.route("/coins", methods=["GET"])
def get_coins():
    from app.trading import get_current_prices
    target_coins = ["BNB", "BTC", "ETH", "DOGE", "SOL", "XRP"]
    prices = get_current_prices(target_coins)
    logger.info(f"Coins data: {prices}")
    return jsonify({"coins": prices})

@api.route('/api/updateGraph', methods=['POST'])
def update_graph():
    data = request.get_json()
    coin = data.get('coin')
    indicator = data.get('indicator')
    upper = data.get('upper')
    lower = data.get('lower')
    interval = data.get('interval')

    if not (coin and indicator and upper is not None and lower is not None and interval):
        return {"message": "Eksik parametreler"}, 400

    reset_trades(coin)  # Önceki ticareti durdur
    start_trading(coin, indicator, upper, lower, interval)

    return {"message": f"{coin} için ticaret algoritması güncellendi ve yeniden başlatıldı"}, 200
