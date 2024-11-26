<template>
  <div class="control-bar-c">
    <!-- Coin Adı -->
    <span>{{ coin }}</span>

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
      <UIInput v-model="upper" label="upper" />
      <UIInput v-model="lower" label="lower" />
    </div>

    <!-- Time Interval Dropdown -->
    <Dropdown
      class="dropdown"
      id="interval"
      label="Time Intervals"
      :options="intervals"
      v-model="selectedInterval"
    />

    <!-- Update Graph Button -->
    <button class="update-button" @click="updateGraph">Update Graph</button>

    <!-- Ekranda Tüm Verileri Göster -->
    <div class="model-display">
      <h3>Selected Data:</h3>
      <p><strong>Coin:</strong> {{ coin }}</p>
      <p><strong>Indicator:</strong> {{ selectedIndicator }}</p>
      <p><strong>Upper Bound:</strong> {{ upper }}</p>
      <p><strong>Lower Bound:</strong> {{ lower }}</p>
      <p><strong>Time Interval:</strong> {{ selectedInterval }}</p>
    </div>
  </div>
</template>

<script lang="ts">
import Dropdown from './DropDown.vue'
import UIInput from './Input.vue'
import axios from 'axios'

export default {
  name: 'ControlBar',
  components: {
    Dropdown,
    UIInput,
  },
  props: {
    coin: { type: String, required: true },
    indicators: { type: Array, required: true },
    indicatorValues: { type: Object, required: true },
    intervals: { type: Array, required: true },
  },
  data() {
    return {
      selectedIndicator: 'RSI', // Varsayılan indikatör
      selectedInterval: '5m', // Varsayılan zaman aralığı
      upper: this.indicatorValues.upper || 70, // Varsayılan üst sınır
      lower: this.indicatorValues.lower || 30, // Varsayılan alt sınır
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
        // Backend'e POST isteği gönder
        const response = await axios.post('/api/updateGraph', payload)
        console.log('Graph updated:', response.data)
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
  gap: 1rem;
  margin-bottom: 1rem;
  margin-top: 1rem;
  padding: 1rem;
  background-color: #1b2126;
  color: aliceblue;
  border-radius: 8px;
  text-align: center;
  flex-direction: row;

  align-items: center;

  button {
    background-color: #06121e;
    color: aliceblue;
    width: 100px;
    height: 50px;
    border-radius: 16px;
    border: 1px solid aliceblue;
  }
  .input-field {
    display: flex;
    flex-direction: row;
  }
  .graph-area {
    margin-top: 1rem;
  }
}
</style>
