from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from waitress import serve
from app.api import api  # api.py'deki Blueprint'i import et

# Flask uygulaması başlatılıyor
app = Flask(__name__)

# Swagger'ı etkinleştir
swagger = Swagger(app)

# CORS ayarları
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})

# API Blueprint'ini uygulamaya dahil et
app.register_blueprint(api)

# Ticaret algoritmasını arka planda başlat
def start_trading_thread(coin, indicator, upper, lower, interval):
    try:
        from app.trading import start_trading  # Burada içeri aktarın
        print(f"Başlatılıyor: {coin}, {indicator}, {upper}, {lower}, {interval}")
        start_trading(coin, indicator, upper, lower, interval)
    except Exception as e:
        print(f"Ticaret başlatılırken hata oluştu: {e}")

# Anasayfa rotası
@app.route("/")
def home():
    return {"message": "Coin Dashboard API is running"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
