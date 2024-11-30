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
    <div v-for="coin in coinList" :key="coin.name" class="coin-section">
      <ControlBar
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
        { id: 3, name: 'BNB' },
        { id: 4, name: 'SOL' },
        { id: 5, name: 'XRB' },
        { id: 6, name: 'DOGE' },
      ],
      backtestCoins: ['ETH', 'BTC', 'BNB', 'SOL', 'XRB', 'DOGE'],
      coins: [],
      tradesByCoin: reactive<{ [key: string]: Trade[] }>({}),

      backtests: [],
      trades: [], // İşlemler
      indicators: ['RSI', 'MACD', 'Bollinger Bands'], // İndikatör türleri

      // ref kullanarak
      indicatorValues: ref<{
        [key: string]: { upper: number; lower: number }
      }>({
        ETH: { upper: 70, lower: 30 },
        BTC: { upper: 60, lower: 40 },
        BNB: { upper: 70, lower: 30 },
        SOL: { upper: 70, lower: 30 },
        XRB: { upper: 70, lower: 30 },
        DOGE: { upper: 70, lower: 30 },
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
</style>
