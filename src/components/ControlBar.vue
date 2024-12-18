<template>
  <div class="control-bar-container">
    <h2>Control</h2>
    <div class="control-bar">
      <span class="coin-name">{{ coin }}</span>

      <!-- Indicator Dropdown -->
      <Dropdown
        class="dropdown"
        id="indicator"
        label="Indicator Type"
        :options="indicators"
        v-model="selectedIndicator"
      />

      <!-- Input Field for indicators -->
      <div class="input-fields">
        <div v-if="selectedIndicator === 'RSI'">
          <UIInput v-model="upper" label="Upper Bound:" />
          <UIInput v-model="lower" label="Lower Bound: " />
        </div>
        <div v-if="selectedIndicator === 'MACD'"></div>
        <div v-if="selectedIndicator === 'Moving Average'">
          <UIInput v-model="upper" label="Period:" />
        </div>
        <div v-if="selectedIndicator === 'Exponential Moving Average'">
          <UIInput v-model="upper" label="Period:" />
        </div>
        <div v-if="selectedIndicator === 'Stochastic RSI'">
          <UIInput v-model="upper" label="Upper Bound:" />
          <UIInput v-model="lower" label="Lower Bound: " />
        </div>
        <div v-if="selectedIndicator === 'Average Directional Index'">
          <UIInput v-model="upper" label="Strong Trend:" />
          <UIInput v-model="lower" label="Weak Trend: " />
        </div>
        <div v-if="selectedIndicator === 'Volume Weighted Average Price'">
          <UIInput v-model="lower" label="Weak Trend: " />
        </div>
        <div v-if="selectedIndicator === 'Commodity Channel Index'">
          <UIInput v-model="upper" label="Overbought:" />
          <UIInput v-model="lower" label="Oversold: " />
        </div>
      </div>

      <!-- Time Interval Dropdown -->
      <Dropdown
        class="dropdown"
        id="interval"
        label="Time Interval"
        :options="intervals"
        v-model="selectedInterval"
      />

      <!-- Start Button -->
      <button class="start-button" @click="updateGraph">Start</button>
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
import { Trade } from 'src/types/Trade'
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
    trades: { type: Array as () => Trade[], required: true },
    defaultSettings: { type: Object, required: true },
  },
  data() {
    return {
      selectedIndicator: this.defaultSettings.indicator || 'RSI',
      selectedInterval: this.defaultSettings.interval || '5m',
      upper: this.defaultSettings.upper || 70,
      lower: this.defaultSettings.lower || 30,
      localTrades: [],
    }
  },
  methods: {
    start() {
      this.updateGraph()
    },
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
.control-bar-container {
  padding: 20px;
  color: #fff;
  width: 100%;

  h2 {
    font-size: 28px;
    margin-bottom: 20px;
    color: #f1f1f1;
    font-weight: 600;
  }

  .control-bar {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    gap: 16px;
    margin-bottom: 1.5rem;
    padding: 20px;
    background-color: #2c3e50;
    border-radius: 10px;
    align-items: center;
  }

  .coin-name {
    font-size: 18px;
    color: #f0b90b;
    font-weight: 600;
    padding-left: 20px;
  }

  .dropdown {
    background-color: #34495e;
    border: none;
    color: #ecf0f1;
    font-size: 16px;
    padding: 10px;
    border-radius: 6px;
    width: 200px;
  }

  .input-fields {
    display: flex;
    flex-direction: column;
    gap: 16px;
    width: 200px;
  }

  .input-fields .input-field {
    margin-top: 10px;
  }

  .start-button {
    background: radial-gradient(circle, #434f63, #2e3842);
    color: white;
    border-radius: 8px;
    border: 1.5px solid aliceblue;
    padding: 10px 20px;
    font-size: 16px;
    margin-right: 30px;
    font-weight: 600;
    cursor: pointer;
    transition:
      background-color 0.3s,
      transform 0.2s;
  }

  .start-button:hover {
    background-color: #3e8375;
    transform: scale(1.05);
  }

  .start-button:active {
    transform: scale(0.98);
  }

  .results {
    display: flex;
    gap: 16px;
    justify-content: space-between;
    margin-top: 30px;
  }

  .results > * {
    flex: 1;
  }

  @media (max-width: 768px) {
    .results {
      flex-direction: column;
    }

    .results > * {
      max-width: 100%;
    }
  }
}
</style>
