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

      <!-- Input Field for RSI -->
      <div class="input-field" v-if="selectedIndicator === 'RSI'">
        <UIInput v-model="upper" label="Upper Bound:" />
        <UIInput v-model="lower" label="Lower Bound: " />
      </div>
      <div class="input-field" v-if="selectedIndicator === 'MACD'">
        <UIInput v-model="upper" label="High Price:" />
        <UIInput v-model="lower" label="Close Price: " />
      </div>
      <div class="input-field" v-if="selectedIndicator === 'Bollinger Bands'">
        <UIInput v-model="upper" label="Upper Band:" />
        <UIInput v-model="lower" label="Lower Band: " />
      </div>
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
  color: aliceblue;
  margin-top: 1rem;
  /*background: linear-gradient(135deg, #2e3b4e, #4f5b6e);*/
  h2 {
    color: white; /* Başlık rengini beyaz yap */
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
      color: yellow;
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
    justify-content: space-between;
    align-items: flex-start;
    gap: 20px;
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
    flex: 1; /* TradeHistory'ye daha az genişlik verir */
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
