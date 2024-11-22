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
          <!-- price kontrolü -->
          <td :class="{ up: coin.change > 0, down: coin.change < 0 }">
            {{ (coin.change || 0).toFixed(2) }}%
            <!-- change kontrolü -->
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import api from '../services/api'
import { Coin } from '../types/Coin'

export default {
  name: 'CoinList',
  setup() {
    const coins = ref<Coin[]>([]) // Coin türünde bir dizi
    let intervalId: number | null = null // Interval ID'yi saklama
    watch(
      () => coins.value,
      (newValue) => {
        console.log('Coin listesi güncellendi:', newValue)
      },
    )
    const fetchCoins = async () => {
      try {
        const response = await api.get('/coins')
        console.log('Gelen veri:', response.data)

        // `response.data.coins` dizisini alıyoruz
        coins.value = response.data.coins.map((item: any) => ({
          symbol: item.symbol,
          price: item.price || 0,
          change: item.change || 0,
        }))
      } catch (error) {
        console.error('Coin verisi alınamadı:', error)
      }
    }

    onMounted(() => {
      fetchCoins()
      intervalId = setInterval(fetchCoins, 5000) as unknown as number
    })

    onUnmounted(() => {
      if (intervalId !== null) {
        clearInterval(intervalId)
      }
    })

    return { coins }
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
