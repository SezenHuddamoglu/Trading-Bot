<template>
  <div>
    <h2>Coin Fiyatları</h2>
    <table>
      <thead>
        <tr>
          <th>Coin</th>
          <th>Fiyat (USD)</th>
          <th>Değişim (%)</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="coin in coins" :key="coin.symbol">
          <td>{{ coin.symbol }}</td>
          <td>{{ (coin.price || 0).toFixed(2) }}</td>
          <td :class="{ up: coin.change > 0, down: coin.change < 0 }">
            {{ (coin.change || 0).toFixed(2) }}%
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script lang="ts">
import api from '../services/api'
import { Coin } from '../types/Coin'

export default {
  name: 'CoinList',
  data() {
    return {
      coins: [] as Coin[], // Coin verisi burada saklanacak
      intervalId: null as number | null, // interval ID
    }
  },
  methods: {
    async fetchCoins() {
      try {
        const response = await api.get('/coins')
        console.log('Gelen veri:', response.data)

        this.coins = response.data.coins.map((item: any) => ({
          symbol: item.symbol,
          price: item.price || 0,
          change: item.change || 0,
        }))
      } catch (error) {
        console.error('Coin verisi alınamadı:', error)
      }
    },
  },
  mounted() {
    this.fetchCoins() // İlk veri çekme
    this.intervalId = setInterval(this.fetchCoins, 5000) as unknown as number
  },
  beforeUnmount() {
    if (this.intervalId !== null) {
      clearInterval(this.intervalId) // Interval temizleme
    }
  },
}
</script>

<style scoped>
.up {
  color: green;
}
.down {
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
