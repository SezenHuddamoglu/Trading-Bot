<template>
  <div>
    <CoinList :coins="coins" />
    <TradeHistory :trades="trades" />
    <div v-for="coin in coinList" :key="coin.id" class="coin-section">
      <ControlBar
        :coin="coin.name"
        :indicators="indicators"
        :indicator-values="indicatorValues[coin.name]"
        :intervals="intervals"
        @update:graph="updateGraph"
      />
    </div>
    <PriceChart :trades="trades" />
  </div>
</template>

<script lang="ts">
import { fetchCoins, fetchTrades } from '../services/api'
import CoinList from '../components/CoinList.vue'
import TradeHistory from '../components/TradeHistory.vue'
import PriceChart from '../components/PriceChart.vue'
import ControlBar from '../components/ControlBar.vue'

export default {
  name: 'DashboardPage',
  components: { CoinList, TradeHistory, PriceChart, ControlBar },
  data() {
    return {
      coinList: [
        { id: 1, name: 'ETH' },
        { id: 2, name: 'BTC' },
        { id: 3, name: 'BNB' },
        { id: 4, name: 'SOL' },
        { id: 5, name: 'XRB' },
        { id: 6, name: 'DOGE' },
      ],
      coins: [],
      trades: [], // İşlemler
      indicators: ['RSI', 'MACD', 'Bollinger Bands'], // İndikatör türleri

      indicatorValues: {
        ETH: { upper: 70, lower: 30 },
        BTC: { upper: 70, lower: 30 },
        BNB: { upper: 70, lower: 30 },
        SOL: { upper: 70, lower: 30 },
        XRB: { upper: 70, lower: 30 },
        DOGE: { upper: 70, lower: 30 },
      },
      intervalId: null as number | null,
      intervals: ['1m', '5m', '15m', '30m', '45m', '1h'],
    }
  },
  methods: {
    async fetchAllData() {
      try {
        this.coins = await fetchCoins()
        this.trades = await fetchTrades()

        // Her coin için varsayılan değerleri tanımla
        if (!Object.keys(this.indicatorValues).length) {
          this.coins.forEach((coin) => {
            this.$set(this.indicatorValues, coin, { upper: 70, lower: 30 })
          })
        }
      } catch (error) {
        console.error('fetchAllData başarısız:', error)
        if (this.intervalId !== null) {
          clearInterval(this.intervalId)
          this.intervalId = null
        }
      }
    },
    updateGraph({ coin, indicator, values }: { coin: string; indicator: string; values: any }) {
      console.log('Graph updated for:', { coin, indicator, values })
    },
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
</style>
