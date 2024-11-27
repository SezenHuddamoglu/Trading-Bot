<template>
  <div class="control-bar-c">
    <div class="bar">
      <!-- Coin Adı -->
      <span class="coin-name">{{ coin }}</span>

      <!-- Indicator Dropdown -->
      <Dropdown
        class="dropdown"
        id="indicator"
        label="Indicator Type"
        :options="indicators"
        v-model="selectedIndicator"
      />

      <!-- Input Field for RSI -->
      <div class="input-field" v-if="selectedIndicator === 'RSI'">
        <UIInput v-model="upper" label="Upper Bound:" />
        <UIInput v-model="lower" label="Lower Bound: " />
      </div>

      <!-- Time Interval Dropdown -->
      <Dropdown
        class="dropdown"
        id="interval"
        label="Time Interval"
        :options="intervals"
        v-model="selectedInterval"
      />

      <!-- Update Graph Button -->
      <button class="update-button" @click="updateGraph">Update Graph</button>
    </div>
    <div class="results">
      <!-- Price Chart and Trade History -->
      <TradeChart :trades="trades" />
      <TradeHistory :trades="trades" />
    </div>
  </div>
</template>

<script lang="ts">
import Dropdown from './Dropdown.vue'
import UIInput from './Input.vue'
import TradeChart from './TradeChart.vue'
import TradeHistory from './TradeHistory.vue'
import axios from 'axios'

export default {
  name: 'ControlBar',
  components: {
    Dropdown,
    UIInput,
    TradeChart,
    TradeHistory,
  },
  props: {
    coin: { type: String, required: true },
    indicators: { type: Array as () => string[], required: true },
    indicatorValues: { type: Object, required: true },
    intervals: { type: Array as () => string[], required: true },
    trades: { type: Array as () => object[], required: true },
  },
  data() {
    return {
      selectedIndicator: 'RSI',
      selectedInterval: '5m',
      upper: this.indicatorValues.upper || 70,
      lower: this.indicatorValues.lower || 30,
      localTrades: [], // Coin özelinde trade geçmişi
    }
  },
  methods: {
    async updateGraph() {
      const payload = {
        coin: this.coin,
        indicator: this.selectedIndicator,
        upper: this.upper,
        lower: this.lower,
        interval: this.selectedInterval,
      }

      console.log('Graph updated for:', payload)

      try {
        const response = await axios.post('/api/updateGraph', payload)
        this.localTrades = response.data.trades // Backend'den gelen trade verilerini güncelle
      } catch (error) {
        console.error('Error updating graph:', error)
      }
    },
  },
}
</script>

<style>
.control-bar-c {
  display: flex;
  flex-direction: column;
  .bar {
    display: flex;
    gap: 16px;
    margin-bottom: 1rem;
    margin-top: 1rem;
    padding: 1rem;
    background-color: #1b2126;
    color: aliceblue;
    border-radius: 8px;
    text-align: center;
    flex-direction: row;
    justify-content: space-evenly;
    align-items: center;
    .coin-name {
      font-size: 16px;
      font-weight: 600;
    }
    button {
      background-color: #06121e;
      color: aliceblue;
      width: 120px;
      height: 50px;
      border-radius: 16px;
      border: 1.5px solid aliceblue;
      font-size: 14px;
      font-weight: 600;
      padding: 4px;
    }
    .input-field {
      display: flex;
      flex-direction: row;
      gap: 16px;
    }
    .graph-area {
      margin-top: 1rem;
    }
  }
  .results {
    display: flex;
    flex-direction: column;
  }
}
</style>
