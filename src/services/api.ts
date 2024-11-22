// src/services/api.js
import axios from 'axios'

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/', // Backend URL'si
})

export async function fetchCoins() {
  try {
    const response = await api.get('/coins')
    console.log('Gelen veri:', response.data)
    return response.data.coins.map((item: any) => ({
      symbol: item.symbol,
      price: item.price || 0,
      change: item.change || 0,
    }))
  } catch (error) {
    console.error('fetchCoins başarısız:', error)
    throw error // Hata fırlatılarak üst katmanda işlenebilir
  }
}

export async function fetchTrades() {
  try {
    const response = await api.get('/trades')
    console.log('Gelen veri:', response.data)
    return response.data.trades.map((trade: any) => ({
      action: trade.action,
      price: trade.price || 0,
      amount: trade.amount || 0,
      timestamp: trade.timestamp || '',
      indicator: trade.indicator || 'N/A', // Varsayılan değer ekleyebilirsiniz
    }))
  } catch (error) {
    console.error('fetchTrades başarısız:', error)
    throw error // Hata fırlatılarak üst katmanda işlenebilir
  }
}

//checkbackend
export default api
