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
          <td>{{ coin.price.toFixed(2) }}</td>
          <td :class="{ up: coin.change > 0, down: coin.change < 0 }">
            {{ coin.change.toFixed(2) }}%
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script lang="ts">
import { ref, onMounted } from 'vue'
import api from '../services/api'

// Define the Coin type
interface Coin {
  symbol: string
  price: number
  change: number
}

export default {
  name: 'CoinList',
  setup() {
    const coins = ref<Coin[]>([]) // Type the coins array

    const fetchCoins = async () => {
      try {
        const response = await api.get('/coins')
        coins.value = response.data
      } catch (error) {
        console.error('Coin verisi alınamadı:', error)
      }
    }

    onMounted(() => {
      fetchCoins()
      // Veriyi düzenli aralıklarla güncelle
      setInterval(fetchCoins, 5000) // 5 saniyede bir
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
