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

# Anasayfa rotası
@app.route("/")
def home():
    return {"message": "Coin Dashboard API is running"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
