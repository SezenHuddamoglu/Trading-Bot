from fastapi import FastAPI
from app.api import router as api_router
import threading
from app.trading import start_trading
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS ayarları
origins = [
    "http://localhost:8080",  # Vue.js frontend URL'si
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

# Ticaret algoritmasını arka planda başlat
trading_thread = threading.Thread(target=start_trading, daemon=True)
trading_thread.start()

@app.get("/")
def read_root():
    return {"message": "Coin Dashboard API is running"}
