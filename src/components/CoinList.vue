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
import { Coin } from '../types/Coin'

export default {
  name: 'CoinList',
  props: {
    coins: {
      type: Array as () => Coin[],
      required: true,
    },
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
