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
  color: aliceblue;
  margin-top: 1rem;
  h2 {
    color: white; /* Başlık rengini beyaz yap */
    font-family: Arial, sans-serif;
    text-align: start;
    font-size: 20px;
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
    width:;
    height: 40px;
    .coin-name {
      font-size: 16px;
      font-weight: 600;
      color: yellow;
    }
    button {
      background-color: #06121e;
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
