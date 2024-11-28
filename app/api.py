from flask import Blueprint, request, jsonify
import logging
from app.trading import get_trade_history, get_current_prices, start_trading
from app.trading_utils import start_trading_thread
from threading import Thread
import threading

api = Blueprint('api', __name__)

# Logger ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

target_coins = ["BNB", "BTC", "ETH", "DOGE", "SOL", "XRP"]
trade_data = {
    "BTC": {"lock": threading.Lock(), "trades": []},
    "ETH": {"lock": threading.Lock(), "trades": []},
    "BNB": {"lock": threading.Lock(), "trades": []},
    "DOGE": {"lock": threading.Lock(), "trades": []},
    "SOL": {"lock": threading.Lock(), "trades": []},
    "XRP": {"lock": threading.Lock(), "trades": []},
}
def add_trade(coin, trade):
    """Belirtilen coin için trade ekler."""
    if coin not in trade_data:
        print(f"Coin {coin} desteklenmiyor.")
        return
    
    with trade_data[coin]["lock"]:  # Coin'in kilidini al
        trade_data[coin]["trades"].append(trade)  # İşlemi ekle
        print(f"{coin} için yeni trade eklendi: {trade}")
        
@api.route("/trades", methods=["GET"])
def get_trades():
    coin = request.args.get("coin")
    if not coin:
        return {"message": "Eksik parametre: coin"}, 400

    trades = get_trades(coin)
    return jsonify({"coin": coin, "trades": trades})
def update_graph_and_table(coin):
    trades = get_trades(coin)  # Coin'in trade listesini al
    # Tablo ve grafiği güncellemek için gerekli işlemler
    print(f"{coin} için grafik ve tablo güncelleniyor. Toplam işlem: {len(trades)}")


@api.route("/coins", methods=["GET"])
def get_coins():
    prices = get_current_prices(target_coins)
    logger.info(f"Coins data: {prices}")  
    return jsonify({"coins": prices})

@api.route('/api/updateGraph', methods=['POST'])
def update_graph():
    # İstekten gelen parametreleri al
    data = request.get_json()
    coin = data.get('coin')
    indicator = data.get('indicator')
    upper = data.get('upper')
    lower = data.get('lower')
    interval = data.get('interval')

    # Eksik parametre kontrolü
    if not (coin and indicator and upper and lower and interval):
        return {"message": "Eksik parametreler"}, 400

    # İstenen coin'in trade listesi var mı kontrol et
    if coin not in trade_data:
        return {"message": f"{coin} desteklenmiyor."}, 400

    # Ticaret işlemini başlat
    start_trading_thread(coin, indicator, upper, lower, interval)

    return {"message": f"{coin} için ticaret başlatıldı"}, 200

