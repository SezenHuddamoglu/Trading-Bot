from flask import Blueprint, request, jsonify
import logging
from app.trading import backtest_strategy, start_trading, reset_trades, get_trade_history
import pandas as pd

# Create a Blueprint for API routes
api = Blueprint('api', __name__)

# Set up logger configuration
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
                  action:
                    type: string
                  amount:
                    type: number
                  deposit:
                    type: number
                  indicator:
                    type: string
                  price:
                    type: number
                  timestamp:
                    type: string
      400:
        description: Invalid coin parameter
    """
    trade_history = get_trade_history(coin)  # Fetch trade history for the given coin
    return jsonify({"trades": trade_history})

@api.route("/trades", methods=["GET"])
def get_trades():
    """
    Get the trade history for all coins.
    """
    from app.trading import get_trade_history
    trades = get_trade_history()  # Fetch trade history for all coins
    logger.info(f"Trades data: {trades}")
    return jsonify({"trades": trades})

@api.route("/coins", methods=["GET"])
def get_coins():
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
                  change:
                    type: number
                  coin:
                    type: string
                  price:
                    type: number
      500:
        description: Internal server error while fetching coin prices
    """
     from app.trading import get_current_prices
     target_coins = ["ETH", "BTC", "AVA", "FET", "SOL", "RENDER", 'AVAX']  # Define target coins
     prices = get_current_prices(target_coins)  # Fetch current prices
     logger.info(f"Coins data: {prices}")
     return jsonify({"coins": prices})

@api.route('/updateGraph', methods=['POST'])
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

    # Validate all required parameters
    if not (coin and indicator and upper is not None and lower is not None and interval):
        return {"message": "Missing parameters"}, 400

    reset_trades(coin)  # Reset trades for the specified coin
    start_trading(coin, indicator, upper, lower, interval)  # Start trading with updated parameters

    return {"message": f"Trading algorithm updated and restarted for {coin}"}, 200

@api.route('/backtest', methods=['POST'])
def backtest():
    """
    Perform a backtest based on provided parameters.
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
              description: The coin to backtest (e.g., BTC, ETH)
            indicator:
              type: string
              description: The indicator to use for backtesting (e.g., RSI, MACD)
            upper:
              type: number
              description: The upper threshold for the indicator
            lower:
              type: number
              description: The lower threshold for the indicator
            interval:
              type: string
              description: The interval for the backtest (e.g., 1m, 5m, 1h)
            balance:
              type: number
              description: The initial balance
          required:
            - coin
            - indicator
            - upper
            - lower
            - interval
            - balance
    responses:
      200:
        description: Successfully performed backtest
        schema:
          type: object
          properties:
            result:
              type: object
              description: The result of the backtest
      400:
        description: Missing or invalid parameters
    """
    data = request.get_json()
    coin = data.get('coin')
    indicator = data.get('indicator')
    upper = data.get('upper')
    lower = data.get('lower')
    interval = data.get('interval')
    balance = data.get('balance')
  
    # Validate all required parameters
    if not (coin and indicator and upper is not None and lower is not None and interval and balance is not None):
        return {"message": "Missing or invalid parameters"}, 400

    try:
        # Perform backtest
        backtest_result = backtest_strategy(coin, indicator, upper, lower, interval, balance)
        return jsonify({"result": backtest_result}), 200
    except Exception as e:
        logger.error(f"Backtest error: {e}")
        return {"message": "An error occurred during backtesting"}, 500
