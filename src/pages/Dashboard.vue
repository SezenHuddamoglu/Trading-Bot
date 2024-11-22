<!-- src/pages/Dashboard.vue -->
<template>
  <div>
    <CoinList />
    <TradeHistory />
    <PriceChart />
  </div>
</template>

<script lang="ts">
import CoinList from '../components/CoinList.vue'
import PriceChart from '../components/PriceChart.vue'
import TradeHistory from '../components/TradeHistory.vue'

export default {
  name: 'DashboardPage',
  components: { CoinList, PriceChart, TradeHistory },
}
</script>

<style scoped>
/* İsteğe bağlı stil eklemeleri */
</style>
