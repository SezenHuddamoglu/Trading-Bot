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
        <UIInput v-model="upperData" label="High Price:" />
        <UIInput v-model="lowerData" label="Close Price: " />
        <UIInput v-model="balance" label="InitialBalance: " />
      </div>
      <div class="input-field" v-if="selectedIndicator === 'Bollinger Bands'">
        <UIInput v-model="upperData" label="Upper Band:" />
        <UIInput v-model="lowerData" label="Lower Band: " />
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
      <TradeChart :trades="localTrades" />
    </div>
  </div>
</template>

<script lang="ts">
import Dropdown from './Dropdown.vue'
import UIInput from './Input.vue'
import { fetchBacktest } from '../services/api'
import TradeChart from './TradeChart.vue'
// import TradeHistory from './TradeHistory.vue'

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
      totalProfit: 0,
    }
  },

  methods: {
    async startBacktest() {
      try {
        const payload = {
          coin: this.selectedCoin,
          indicator: this.selectedIndicator,
          upper: this.upperData,
          lower: this.lowerData,
          balance: this.balance,
          interval: this.selectedInterval,
        }
        console.log(payload)
        const result = await fetchBacktest(payload)
        this.totalProfit = result.profit
        this.localTrades = result.trades
      } catch (error) {
        console.error('Backtest çalıştırılırken hata oluştu:', error)
      }
    },
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
    background-color: #295F98;
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
