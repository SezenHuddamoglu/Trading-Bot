<template>
  <div class="backtest-bar">
    <h2>Backtest Control</h2>
    <div class="bar">
      <Dropdown
        class="dropdown"
        id="coin"
        label="Coin Type"
        :options="coinList"
        v-model="selectedCoin"
      />

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
        <UIInput v-model="upperData" label="Upper Bound:" />
        <UIInput v-model="lowerData" label="Lower Bound: " />
        <UIInput v-model="balance" label="Initial Balance: " />
      </div>
      <div class="input-field" v-if="selectedIndicator === 'MACD'">
        <UIInput v-model="balance" label="InitialBalance: " />
      </div>
      <div class="input-field" v-if="selectedIndicator === 'Bollinger Bands'">
        <UIInput v-model="upperData" label="Upper Band:" />
        <UIInput v-model="lowerData" label="Lower Band: " />
        <UIInput v-model="balance" label="InitialBalance: " />
      </div>
      <div class="input-field" v-if="selectedIndicator === 'Moving Average'">
        <UIInput v-model="upperData" label="Period:" />
        <UIInput v-model="balance" label="InitialBalance: " />
      </div>
      <div class="input-field" v-if="selectedIndicator === 'Exponential Moving Average'">
        <UIInput v-model="upperData" label="Period:" />
        <UIInput v-model="balance" label="InitialBalance: " />
      </div>
      <div class="input-field" v-if="selectedIndicator === 'Stochastic RSI'">
        <UIInput v-model="upperData" label="Upper Bound:" />
        <UIInput v-model="lowerData" label="Lower Bound: " />
        <UIInput v-model="balance" label="InitialBalance: " />
      </div>
      <div class="input-field" v-if="selectedIndicator === 'Average Directional Index'">
        <UIInput v-model="upperData" label="Strong Trend:" />
        <UIInput v-model="lowerData" label="Weak Trend: " />
      </div>
      <div class="input-field" v-if="selectedIndicator === 'Volume Weighted Average Price'">

        <UIInput v-model="balance" label="InitialBalance: " />
      </div>
      <div class="input-field" v-if="selectedIndicator === 'Commodity Channel Index'">
        <UIInput v-model="upperData" label="Overbougth:" />
        <UIInput v-model="lowerData" label="Oversold: " />
        <UIInput v-model="balance" label="InitialBalance: " />
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
      <button class="update-button" @click="startBacktest">Start</button>
    </div>
    <div class="results">
      <div>Total Profit: {{ totalProfit }}</div>

      <TradeChart :trades="trades" class="chart" />
    </div>
  </div>
</template>

<script lang="ts">
import Dropdown from './Dropdown.vue'
import UIInput from './Input.vue'

import TradeChart from './TradeChart.vue'
//import TradeHistory from './TradeHistory.vue'
import { Trade } from '../types/Trade'

export default {
  name: 'ControlBar',
  components: {
    Dropdown,
    UIInput,
    TradeChart,
    // TradeHistory,
  },
  props: {
    coinList: { type: Array as () => string[], required: true },
    indicators: { type: Array as () => string[], required: true },
    upper: { type: String, required: true },
    lower: { type: String, required: true },
    intervals: { type: Array as () => string[], required: true },
    //trades: { type: Array as () => object[], required: true },
    initialBalance: { type: String, required: true },
    totalProfit: Number,
    trades: { type: Array as () => Trade[], required: true },
  },
  data() {
    return {
      selectedCoin: 'ETH',
      selectedIndicator: 'RSI',
      selectedInterval: '5m',
      upperData: 70,
      lowerData: 30,
      localTrades: [], // Coin özelinde trade geçmişi
      balance: 10000,
    }
  },

  methods: {
    startBacktest() {
      const params = {
        coin: this.selectedCoin,
        indicator: this.selectedIndicator,
        balance: this.balance,
        interval: this.selectedInterval,
        lower: this.lowerData,
        upper: this.upperData, // upperData doğru alan olmalı
        // lowerData doğru alan olmalı
        // initialBalance beklenen ad
      }
      this.$emit('fetch-backtest', params)
    },
  },
  mounted() {
    //this.startBacktest()
  },
}
</script>

<style>
.backtest-bar {
  display: flex;
  flex-direction: column;
  color: aliceblue;
  margin-top: 100px;

  h2 {
    color: aliceblue; /* Başlık rengini beyaz yap */
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
    height: 60px;

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
    .input-field input {
      background-color: #2c3338; /* Gri bir arka plan rengi */
      color: aliceblue; /* Beyaz yazı rengi */
      border: 1px solid #444; /* Gri kenarlık */
      border-radius: 4px; /* Hafif yuvarlatılmış kenarlar */
      padding: 4px; /* İçerik ile kenar boşluğu */
      font-size: 12px; /* Yazı boyutunu küçült */
    }

    .input-field label {
      font-size: 14px;
      margin-right: 4px;
      color: aliceblue;
    }
    .input-field input:focus,
    .dropdown select:focus {
      outline: none; /* Odaklandığında varsayılan çerçeve kaldırılır */
      border: 1px solid aliceblue; /* Odaklandığında kenarlık beyaz olur */
    }
    .dropdown select {
      background-color: #2c3338; /* Gri bir arka plan rengi */
      color: aliceblue; /* Beyaz yazı rengi */
      border: 1px solid #444; /* Gri kenarlık */
      border-radius: 4px; /* Hafif yuvarlatılmış kenarlar */
      padding: 4px; /* İçerik ile kenar boşluğu */
      font-size: 14px; /* Yazı boyutunu küçült */
    }
    .dropdown input {
      width: 100px; /* Genişliği azaltarak daha ince görünmesini sağlayın */
      height: 30px; /* Yüksekliği azaltın */
      padding: 4px 8px; /* İçerik ile kenar arasındaki boşluğu küçültün */
      font-size: 14px; /* Yazı boyutunu küçültün */
      border: 1px solid #ccc; /* İnce bir kenarlık ekleyin */
      border-radius: 4px; /* Hafif yuvarlatılmış köşeler */
      background-color: #1b2126; /* Arka plan rengini aynı temaya uygun hale getirin */
      color: aliceblue;
    }
    .dropdown label {
      font-size: 14px;
      margin-right: 4px;
      color: aliceblue;
    }
    .graph-area {
      margin-top: 1rem;
    }
  }
  .results {
    display: flex;
    flex-direction: column;
    /* justify-content: space-between;
    align-items: flex-start; */
    gap: 20px;
    margin-top: 20px;

    .chart {
      width: 1200px;
    }
  }
}
</style>
