<template>
  <div>
    <CoinList :coins="coins" />
    <TradeHistory :trades="trades" />
    <PriceChart :trades="trades" />
  </div>
</template>

<script lang="ts">
import { fetchCoins, fetchTrades } from '../services/api'
import CoinList from '../components/CoinList.vue'
import TradeHistory from '../components/TradeHistory.vue'
import PriceChart from '../components/PriceChart.vue'

export default {
  name: 'DashboardPage',
  components: { CoinList, TradeHistory, PriceChart },
  data() {
    return {
      coins: [],
      trades: [],
      intervalId: null as number | null,
    }
  },
  methods: {
    async fetchAllData() {
      try {
        // Merkezi fonksiyonlardan veriyi çekiyoruz
        this.coins = await fetchCoins()
        this.trades = await fetchTrades()
      } catch (error) {
        console.error('fetchAllData başarısız:', error)

        // Hata durumunda interval'i durdur
        if (this.intervalId !== null) {
          clearInterval(this.intervalId)
          this.intervalId = null
        }
      }
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
