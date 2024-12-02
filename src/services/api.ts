// src/services/api.js
import axios from 'axios'

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/', // Backend URL'si
})

export async function fetchCoins() {
  try {
    const response = await api.get('/api/coins')
    //console.log('Gelen veri:', response.data)
    return response.data.coins.map((item: { symbol: string; price: number; change: number }) => ({
      symbol: item.symbol,
      price: item.price || 0,
      change: item.change || 0,
    }))
  } catch (error) {
    console.error('fetchCoins başarısız:', error)
    throw error // Hata fırlatılarak üst katmanda işlenebilir
  }
}

export async function fetchTrades(coin: string) {
  try {
    const response = await api.get(`/api/trades/${coin}`)
    console.log('Gelen veri:', response.data)

    const trades = Array.isArray(response.data.trades)
      ? response.data.trades
      : Object.values(response.data.trades)

    return trades.map(
      (trade: {
        action: string
        price: number
        amount: number
        timestamp: string
        indicator: string
        balance: number
      }) => ({
        action: trade.action,
        price: trade.price || 0,
        amount: trade.amount || 0,
        timestamp: trade.timestamp || '',
        indicator: trade.indicator || 'N/A',
        deposit: trade.balance || 0,
      }),
    )
  } catch (error) {
    console.error(`Error fetching trades for ${coin}:`, error)
    throw error
  }
}
export async function fetchBacktest(params: {
  coin: string
  indicator: string
  balance: number
  interval: string
  lower: number
  upper: number
}) {
  try {
    const response = await api.post('/api/backtest', params)
    console.log('Gelen veri:', response.data) // Burada gelen veriyi kontrol et
    const result = response.data.result

    // Gelen verileri mapleme
    const backtestData = {
      profit: result.profit || 0,
      trades: Array.isArray(result.trades)
        ? result.trades.map(
            (trade: {
              action: string
              price: number
              amount: number
              timestamp: string
              indicator: string
              deposit: number
            }) => ({
              action: trade.action,
              price: trade.price || 0,
              amount: trade.amount || 0,
              timestamp: trade.timestamp || '',
              indicator: trade.indicator || 'N/A',
              deposit: trade.deposit || 0,
            }),
          )
        : [],
    }
    console.log('Maplanmış backtest verisi:', backtestData) // Maplenmiş veri
    return backtestData
  } catch (error) {
    console.error('fetchBacktest başarısız:', error)
    throw error
  }
}
// export async function fetchBacktest(params) {
//   try {
//     const response = await axios.post('http://127.0.0.1:8000/api/backtest', params)
//     return response.data // Yanıt buradan gelmezse undefined olur.
//   } catch (error) {
//     console.error('fetchBacktest başarısız:', error)
//     throw error // Hata yeniden fırlatılmalı.
//   }
// }

//checkbackend
export default api
