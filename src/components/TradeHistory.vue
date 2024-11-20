<template>
  <div>
    <h2>İşlem Geçmişi</h2>
    <table>
      <thead>
        <tr>
          <th>Zaman</th>
          <th>İşlem</th>
          <th>Fiyat (USD)</th>
          <th>Miktar</th>
          <th>Göstergeler</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="trade in trades" :key="trade.timestamp">
          <td>{{ formatDate(trade.timestamp) }}</td>
          <td :class="{ buy: trade.action === 'Buy', sell: trade.action === 'Sell' }">
            {{ trade.action }}
          </td>
          <td>{{ trade.price.toFixed(2) }}</td>
          <td>{{ trade.amount.toFixed(4) }}</td>
          <td>{{ trade.indicator }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script lang="ts">
import { ref, onMounted } from 'vue'
import api from '../services/api'
import { Trade } from '../types/Trade'

export default {
  name: 'TradeHistory',
  setup() {
    const trades = ref<Trade[]>([]) // trades dizisinin tipi belirleniyor

    // Trades verisini almak için fetchTrades fonksiyonu
    const fetchTrades = async () => {
      try {
        const response = await api.get('/trades')
        trades.value = response.data
      } catch (error) {
        console.error('İşlem geçmişi alınamadı:', error)
      }
    }

    // Date formatı, timestamp türü number olarak belirtiliyor
    const formatDate = (timestamp: number) => {
      const date = new Date(timestamp)
      return date.toLocaleString()
    }

    // Veriyi düzenli aralıklarla güncelle
    onMounted(() => {
      fetchTrades()
      setInterval(fetchTrades, 5000) // 5 saniyede bir
    })

    return { trades, formatDate }
  },
}
</script>

<style scoped>
.buy {
  color: green;
}
.sell {
  color: red;
}
table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}
th,
td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: center;
}
th {
  background-color: #f2f2f2;
}
</style>
