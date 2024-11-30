from flask import Blueprint, request, jsonify
import logging
from app.trading import start_trading, reset_trades, get_trade_history
from app.trading import load_historical_data
from app.trading import perform_backtest
import pandas as pd


api = Blueprint('api', __name__)

# Logger ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


@api.route("/trades/<coin>", methods=["GET"])
def get_trades_for_coin(coin):
    """
    Get the trade history for a specific coin
    ---
    parameters:
      - name: coin
        in: path
        description: The coin for which to fetch trade history (e.g., BTC, ETH)
        required: true
        type: string
    responses:
      200:
        description: Successfully fetched trade history
        schema:
          type: object
          properties:
            trades:
              type: array
              items:
                type: object
                properties:
                  timestamp:
                    type: string
                  trade_type:
                    type: string
                  price:
                    type: number
                  quantity:
                    type: number
      400:
        description: Invalid coin parameter
    """
    trade_history = get_trade_history(coin)
    return jsonify({"trades": trade_history})

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
    """
    Get the current prices of the target coins
    ---
    responses:
      200:
        description: Successfully fetched current coin prices
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
                    type: number
      500:
        description: Internal server error while fetching coin prices
    """
    prices = get_current_prices(target_coins)
    logger.info(f"Coins data: {prices}")
    return jsonify({"coins": prices})

@api.route('/api/updateGraph', methods=['POST'])
def update_graph():
    """
    Update the trading algorithm with new parameters
    ---
    parameters:
      - name: coin
        in: body
        description: The coin to trade (e.g., BTC, ETH)
        required: true
        type: string
      - name: indicator
        in: body
        description: The indicator to use for trading (e.g., RSI, MACD)
        required: true
        type: string
      - name: upper
        in: body
        description: The upper threshold for the indicator
        required: true
        type: float
      - name: lower
        in: body
        description: The lower threshold for the indicator
        required: true
        type: float
      - name: interval
        in: body
        description: The trading interval (e.g., 1m, 5m, 1h)
        required: true
        type: string
    responses:
      200:
        description: Trading algorithm updated successfully
      400:
        description: Missing or invalid parameters
    """
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
