<template>
  <div>
    <!-- Kontrol Barı -->
    <div class="control-bar">
      <h2>Control</h2>
      <div>
        <label for="coin">Coin Type:</label>
        <select v-model="selectedCoin" id="coin">
          <option v-for="coin in coins" :key="coin" :value="coin">{{ coin }}</option>
        </select>
      </div>
      <div>
        <label for="indicator">Indicator Type:</label>
        <select v-model="selectedIndicator" id="indicator">
          <option v-for="indicator in indicators" :key="indicator" :value="indicator">{{ indicator }}</option>
        </select>
      </div>
      <div v-if="selectedIndicator === 'RSI'" class="indicator-values">
        <label for="upper-bound">Upper:</label>
        <input
          type="number"
          v-model.number="indicatorValues.upper"
          id="upper-bound"
          placeholder="Enter upper bound"
        />
        <label for="lower-bound">Lower:</label>
        <input
          type="number"
          v-model.number="indicatorValues.lower"
          id="lower-bound"
          placeholder="Enter lower bound"
        />
      </div>
      <button @click="updateGraph">Update Graph</button>
    </div>

    <!-- Grafik Alanı -->
    <div class="graph-area">
      <GraphComponent
        :coin="selectedCoin"
        :indicator="selectedIndicator"
        :indicator-values="indicatorValues"
      />
    </div>
  </div>
</template>

<script>
import PriceChart from "./PriceChart.vue"; // Grafik bileşeni

export default {
  components: { PriceChart },
  data() {
    return {
      coins: ["ETH", "BTC", "BNB", "SOL", "XRB", "DOGE"], // Coin seçenekleri
      indicators: ["RSI", "MACD", "Bollinger Bands"], // İndikatör seçenekleri
      selectedCoin: "ETH", // Varsayılan coin
      selectedIndicator: "RSI", // Varsayılan indikatör
      indicatorValues: { upper: 70, lower: 30 }, // İndikatör değerleri
    };
  },
  methods: {
    updateGraph() {
      // Burada, seçilen coin ve indikatörle grafiği güncelleyebilirsiniz
      console.log("Graph updated with:", {
        coin: this.selectedCoin,
        indicator: this.selectedIndicator,
        values: this.indicatorValues,
      });
    },
  },
};
</script>

<style>
.control-bar {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  margin-top: 1rem;
  padding: 1rem;
  background-color: #1b2126;
  color:aliceblue;
  border-radius: 8px;
  text-align: center;
}
button{
  background-color: #06121e;
  color:aliceblue;

}
.graph-area {
  margin-top: 1rem;
}
</style>
