<template>
  <div>
    <h2>Trading History</h2>
    <table>
      <thead>
        <tr>
          <th>Time</th>
          <th>Trade</th>
          <th>Price(USD)</th>
          <th>Amount</th>
          <th>Indicators</th>
          <th>Total Deposit</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="trade in trades" :key="trade.timestamp">
          <td>{{ formatDate(trade.timestamp) }}</td>
          <td :class="{ buy: trade.action === 'Buy', sell: trade.action === 'Sell' }">
            {{ trade.action }}
          </td>
          <!-- Check if price is defined before using toFixed -->
          <td>
            {{ trade.price !== undefined && trade.price !== null ? trade.price.toFixed(2) : 'N/A' }}
          </td>
          <!-- Check if amount is defined before using toFixed -->
          <td>
            {{
              trade.amount !== undefined && trade.amount !== null ? trade.amount.toFixed(4) : 'N/A'
            }}
          </td>
          <td>{{ trade.indicator }}</td>
          <td>
            {{
              trade.deposit !== undefined && trade.deposit !== null
                ? trade.deposit.toFixed(4)
                : 'N/A'
            }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script lang="ts">
import { Trade } from '../types/Trade'

export default {
  name: 'TradeHistory',
  props: {
    trades: {
      type: Array as () => Trade[],
      required: true,
    },
  },
  methods: {
    formatDate(timestamp: number) {
      const date = new Date(timestamp)
      return date.toLocaleString()
    },
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

th {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: center;
  color: black;
  background-color: #f2f2f2;
}
td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: center;
  color: white;
}
h2 {
  color: #f2f2f2;
}
</style>
