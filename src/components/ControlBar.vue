<template>
  <div class="control-bar-c">
    <h2>Control</h2>
    <div class="bar">
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
      <div class="input-field" v-if="selectedIndicator === 'RSI'">
        <UIInput v-model="upper" label="Upper Bound:" />
        <UIInput v-model="lower" label="Lower Bound: " />
      </div>
      <div class="input-field" v-if="selectedIndicator === 'MACD'"></div>

      <div class="input-field" v-if="selectedIndicator === 'Moving Average'">
        <UIInput v-model="upper" label="Period:" />
      </div>
      <div class="input-field" v-if="selectedIndicator === 'Exponential Moving Average'">
        <UIInput v-model="upper" label="Period:" />
      </div>
      <div class="input-field" v-if="selectedIndicator === 'Stochastic RSI'">
        <UIInput v-model="upper" label="Upper Bound:" />
        <UIInput v-model="lower" label="Lower Bound: " />
      </div>
      <div class="input-field" v-if="selectedIndicator === 'Average Directional Index'">
        <UIInput v-model="upper" label="Strong Trend:" />
        <UIInput v-model="lower" label="Weak Trend: " />
      </div>
      <div class="input-field" v-if="selectedIndicator === 'Volume Weighted Average Price'">
        <UIInput v-model="lower" label="Weak Trend: " />
      </div>
      <div class="input-field" v-if="selectedIndicator === 'Commodity Channel Index'">
        <UIInput v-model="upper" label="Overbougth:" />
        <UIInput v-model="lower" label="Oversold: " />
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
      <button class="update-button" @click="updateGraph">Start</button>
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
.control-bar-c {
  display: flex;
  flex-direction: column;
  color: aliceblue;
  margin-top: 1rem;

  h2 {
    color: white;
    font-family: Arial, sans-serif;
    text-align: start;
    font-size: 25px;
  }
  .bar {
    display: flex;
    gap: 16px;
    margin-bottom: 1rem;
    padding: 1rem;
    background-color: #1b2126;
    color: aliceblue;
    border-radius: 8px;
    text-align: center;
    flex-direction: row;
    justify-content: space-evenly;
    align-items: center;

    height: 40px;
    .coin-name {
      font-size: 16px;
      font-weight: 600;
      color: #f0b90b;
    }
    button {
      background: radial-gradient(circle, #434f63, #2e3842);
      color: aliceblue;
      width: 100px;
      height: 40px;
      border-radius: 16px;
      border: 1.5px solid aliceblue;
      font-size: 14px;
      font-weight: 600;
      padding: 4px;
      cursor: pointer;
    }
    .input-field {
      display: flex;
      flex-direction: row;
      gap: 8px;
    }

    .graph-area {
      margin-top: 1rem;
    }
  }
  .results {
    display: flex;
    flex-direction: row;
    justify-content: space-evenly;
    align-items: flex-start;
    /* gap: 20px; */
    margin-top: 20px;
  }
  .results > * {
    flex: 1;
    max-width: 45%;
  }
  .results > *:first-child {
    flex: 2;
    min-width: 60%;
  }

  .results > *:last-child {
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
