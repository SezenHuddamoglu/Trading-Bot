from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import threading
from app.trading import start_trading
from app.api import api_router  # FastAPI API Router'ını buraya import edin.

app = FastAPI()

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vue.js frontend URL'sine izin veriyoruz.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Router'ı ekleyin
app.include_router(api_router)

# Ticaret algoritmasını arka planda başlat
def start_trading_thread():
    start_trading()  # Ticaret algoritmasını başlatma fonksiyonu.

# Arka planda ticaret algoritmasını başlat
trading_thread = threading.Thread(target=start_trading_thread, daemon=True)
trading_thread.start()

@app.get("/")
def home():
    return {"message": "Coin Dashboard API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
