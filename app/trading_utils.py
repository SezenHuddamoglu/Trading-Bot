import threading
from app.trading import start_trading

threads = {}

def start_trading_thread(coin, indicator, upper, lower, interval):
    global threads
    if coin in threads:
        print(f"Ticaret zaten başlatıldı: {coin}")
        return  # Aynı coin için tekrar thread başlatmayın
    
    def trading_task():
        try:
            start_trading(coin, indicator, upper, lower, interval)
        except Exception as e:
            print(f"Ticaret başlatılırken hata oluştu: {e}")
        finally:
            # İşlem tamamlanınca thread'i temizle
            threads.pop(coin, None)

    thread = threading.Thread(target=trading_task)
    threads[coin] = thread
    thread.start()
    print(f"{coin} için ticaret başlatıldı")
