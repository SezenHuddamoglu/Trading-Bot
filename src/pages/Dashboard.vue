<template>
  <div>
    <CoinList :coins="coins" />
    <Backtest
      :coinList="backtestCoins"
      :indicators="indicators"
      upper=""
      lower=""
      :intervals="intervals"
      :initialBalance="''"
      :trades="backtests"
    />
    <div class="start-all">
      <p class="text">Tüm coinler ile trade'i başlatmak için tıklayın</p>
      <button class="update-button" @click="startAll">Start</button>
    </div>
    <div v-for="coin in coinList" :key="coin.name" class="coin-section">
      <ControlBar
        ref="controlBars"
        :coin="coin.name"
        :indicators="indicators"
        :indicator-values="indicatorValues[coin.name]"
        :intervals="intervals"
        :trades="tradesByCoin[coin.name] || []"
      />
    </div>
  </div>
</template>

<script lang="ts">
import { fetchCoins, fetchTrades } from '../services/api'
import CoinList from '../components/CoinList.vue'
import ControlBar from '../components/ControlBar.vue'
import { reactive, ref } from 'vue'
import Backtest from '../components/Backtest.vue'
import { Trade } from '../types/Trade'

export default {
  name: 'DashboardPage',
  components: { CoinList, ControlBar, Backtest },
  data() {
    return {
      coinList: [
        { id: 1, name: 'ETH' },
        { id: 2, name: 'BTC' },
        { id: 3, name: 'AVA' },
        { id: 4, name: 'SOL' },
        { id: 5, name: 'RENDER' },
        { id: 6, name: 'FET' },
      ],
      backtestCoins: ['ETH', 'BTC', 'AVA', 'SOL', 'RENDER', 'FET'],
      coins: [],
      tradesByCoin: reactive<{ [key: string]: Trade[] }>({}),

      backtests: [],
      trades: [], // İşlemler
      indicators: [
        'RSI',
        'MACD',
        'Bollinger Bands',
        'Moving Average',
        'Exponential Moving Average',
        'Stochastic RSI',
        'Average Directional Index',
        'Volume Weighted Average Price',
        'Commodity Channel Index',
      ], // İndikatör türleri

      // ref kullanarak
      indicatorValues: ref<{
        [key: string]: { upper: number; lower: number }
      }>({
        ETH: { upper: 70, lower: 30 },
        BTC: { upper: 60, lower: 40 },
        AVA: { upper: 70, lower: 30 },
        SOL: { upper: 70, lower: 30 },
        RENDER: { upper: 70, lower: 30 },
        FET: { upper: 70, lower: 30 },
      }),
      intervalId: null as number | null,
      intervals: ['1m', '5m', '15m', '30m', '45m', '1h'],
    }
  },
  computed: {
    tradesByCoinComputed() {
      // Gereksizse tradesByCoin için kullanılabilir.
      return this.tradesByCoin
    },
  },
  methods: {
    async fetchAllData() {
      try {
        this.coins = await fetchCoins()

        for (const coin of this.coinList) {
          if (!this.tradesByCoin[coin.name]) {
            this.tradesByCoin[coin.name] = [] // Başlangıç değeri belirle
          }
          const trades = await fetchTrades(coin.name)
          this.tradesByCoin[coin.name] = trades
        }
        // Her coin için varsayılan değerleri tanımla
      } catch (error) {
        console.error('fetchAllData başarısız:', error)
        if (this.intervalId !== null) {
          clearInterval(this.intervalId)
          this.intervalId = null
        }
      }
    },
    startAll() {
      const controlBars = this.$refs.controlBars
      if (Array.isArray(controlBars)) {
        controlBars.forEach((controlBar) => {
          if (controlBar && typeof controlBar.start === 'function') {
            controlBar.start()
          }
        })
      }
    },
    // updateGraph({
    //   coin,
    //   indicator,
    //   values,
    // }: {
    //   coin: string
    //   indicator: string
    //   values: { upper: number; lower: number }
    // }) {
    //   console.log('Graph updated for:', { coin, indicator, values })
    // },
  },
  mounted() {
    this.fetchAllData()
    this.intervalId = setInterval(this.fetchAllData, 5000) as unknown as number
  },
  beforeUnmount() {
    if (this.intervalId !== null) {
      clearInterval(this.intervalId)
    }
  },
}
</script>

<style>
.coin-section {
  margin-bottom: 1rem;
}
.start-all {
  margin-top: 100px;
  gap: 32px;
  display: flex; /* Elemanları yan yana yerleştirir */
  justify-content: flex-end; /* Sağ tarafa hizalar */
  align-items: center; /* Dikeyde ortalar */
  width: 100%;

  /* Container'ın genişliği tam olarak 100% */
  .text {
    color: aliceblue;
    font-size: 16px;
    padding: 4px;
    margin-right: 20px; /* Metin ile buton arasına daha fazla boşluk ekler */
  }

  .update-button {
    background-color: aliceblue;
    color: #06121e;
    width: 200px;
    height: 50px;
    border-radius: 16px;
    border: 1.5px solid aliceblue;
    text-align: center;
    font-size: 18px;
    font-weight: 600;
    padding: 10px 20px;
    cursor: pointer;
  }
}
</style>
