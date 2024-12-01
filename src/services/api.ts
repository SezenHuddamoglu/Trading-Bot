// src/services/api.js
import axios from 'axios'

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/', // Backend URL'si
})

export async function fetchCoins() {
  try {
    const response = await api.get('/api/coins')
    console.log('Gelen veri:', response.data)
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
  } catch (error) {
    console.error(`Error fetching trades for ${coin}:`, error)
    throw error
  }
}

//checkbackend
export default api
