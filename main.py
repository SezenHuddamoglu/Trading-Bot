from flask import Flask
from flask_cors import CORS
import threading
from app.trading import start_trading
from app.api import app  # Flask uygulamasını buraya import edin
from flasgger import Swagger

# Swagger'ı etkinleştir
swagger = Swagger(app)

# CORS ayarları
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})

# Ticaret algoritmasını arka planda başlat
def start_trading_thread():
    start_trading()

trading_thread = threading.Thread(target=start_trading_thread, daemon=True)
trading_thread.start()

# Anasayfa rotası
@app.route("/")
def home():
    return {"message": "Coin Dashboard API is running"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
