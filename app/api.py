from flask import Blueprint, request, jsonify
import logging
from app.trading import start_trading, reset_trades
from app.trading import load_historical_data
from app.trading import perform_backtest
import pandas as pd

api = Blueprint('api', __name__)

# Logger ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

@api.route('/backtest', methods=['POST'])
def backtest():
    # Kullanıcıdan gelen parametreler
    params = request.json
    coin = params.get("coin")  # Örneğin 'ETH'
    indicator = params.get("indicator")  # 'RSI', 'MACD', 'Bollinger'
    lower_limit = params.get("lower_limit", 30)
    upper_limit = params.get("upper_limit", 70)
    interval = params.get("interval", '1h')  # Default: 1 saatlik veriler
    initial_balance = params.get("initial_balance", 10000)

    # Verileri yükleme (örnek)
    data = load_historical_data(coin)  # Geçmiş verileri yükleme fonksiyonu
    data.index = pd.to_datetime(data['timestamp'])  # Zaman serisi düzenleme
    data = data.set_index('timestamp')

    # Backtest işlemi
    result = perform_backtest(data, initial_balance, indicator, lower_limit, upper_limit, interval)
    
    return jsonify(result)

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
