from flask import Blueprint, request, jsonify
import logging
from app.trading import start_trading, reset_trades, get_trade_history,perform_backtest,load_historical_data
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
    """
    Perform a backtest on historical data for a specific coin and indicator
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            coin:
              type: string
              description: The coin to perform the backtest on (e.g., 'ETH', 'BTC')
              example: "ETH"
            indicator:
              type: string
              description: The indicator to use for backtesting ('RSI', 'MACD', 'Bollinger')
              example: "RSI"
            lower_limit:
              type: number
              description: The lower limit for the indicator
              example: 30
            upper_limit:
              type: number
              description: The upper limit for the indicator
              example: 70
            interval:
              type: string
              description: Time interval for the backtest (e.g., '1h', '1d')
              example: "1h"
            initial_balance:
              type: number
              description: Initial balance for the backtest
              example: 10000
    responses:
      200:
        description: Backtest performed successfully
        schema:
          type: object
          properties:
            total_profit:
              type: number
              description: The total profit or loss from the backtest
              example: 1500.25
            final_balance:
              type: number
              description: The final balance after the backtest
              example: 11500.25
            trades:
              type: array
              description: List of trades executed during the backtest
              items:
                type: object
                properties:
                  timestamp:
                    type: string
                    description: The time of the trade
                  trade_type:
                    type: string
                    description: The type of the trade ('BUY' or 'SELL')
                  price:
                    type: number
                    description: The price at which the trade was executed
                  quantity:
                    type: number
                    description: The quantity traded
      400:
        description: Invalid input parameters
    """
    params = request.json
    coin = params.get("coin")  # Örneğin 'ETH'
    indicator = params.get("indicator")  # 'RSI', 'MACD', 'Bollinger'
    lower_limit = params.get("lower_limit", 30)
    upper_limit = params.get("upper_limit", 70)
    interval = params.get("interval", '1h')  # Default: 1 saatlik veriler
    initial_balance = params.get("initial_balance", 10000)

    # Verileri yükleme (örnek)
    data = load_historical_data(coin,interval)  # Geçmiş verileri yükleme fonksiyonu
    print("---------------",data.columns,"---------------------")
    #data.index = pd.to_datetime(data['timestamp']) 
    #data = data.set_index('timestamp')
    data['Open Time'] = pd.to_datetime(data['Open Time'], unit='ms')  # Eğer zaman damgası milisaniye cinsindense
    data.set_index('Open Time', inplace=True) 

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
