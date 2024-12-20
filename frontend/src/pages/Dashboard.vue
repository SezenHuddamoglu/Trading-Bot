<template>
  <div class="container">
    <CoinList :coins="coins" />
    <Backtest
      :coinList="backtestCoins"
      :indicators="indicators"
      :upper="''"
      :lower="''"
      :intervals="intervals"
      :initialBalance="''"
      :totalProfit="totalProfit"
      :finalBalance="finalBalance"
      :trades="trades"
      @fetch-backtest="handleFetchBacktest"
    />

    <div class="start-all">
      <p class="text">Click to start trading with all coins</p>
      <button class="startAll-button" @click="startAll">Start</button>
    </div>

    <div v-for="coin in coinList" :key="coin.name" class="coin-section">
      <ControlBar
        ref="controlBars"
        :coin="coin.name"
        :indicators="indicators"
        :indicator-values="indicatorValues[coin.name]"
        :intervals="intervals"
        :trades="tradesByCoin[coin.name] || []"
        :defaultSettings="
          defaultIndicatorSettings[coin.name as keyof typeof defaultIndicatorSettings] || {}
        "
      />
    </div>
  </div>
</template>
<script lang="ts">
import { fetchBacktest, fetchCoins, fetchTrades } from '../services/api'
import CoinList from '../components/CoinList.vue'
import ControlBar from '../components/ControlBar.vue'
import Backtest from '../components/Backtest.vue'
import { reactive, ref } from 'vue'
import { Trade } from '../types/Trade'
interface Backtest {
  coin: string
  indicator: string
  balance: number
  interval: string
  lower: number
  upper: number
}

export default {
  name: 'DashboardPage',
  components: { CoinList, ControlBar, Backtest },
  data() {
    return {
      defaultIndicatorSettings: {
        ETH: {
          indicator: 'Stochastic RSI',
          upper: 85,
          lower: 80,
          interval: '1h',
        },
        BTC: {
          indicator: 'Moving Average',
          upper: 50,
          lower: 0,
          interval: '1h',
        },
        AVA: {
          indicator: 'MACD',
          upper: 0,
          lower: 0,
          interval: '30m',
        },
        SOL: {
          indicator: 'Stochastic RSI',
          upper: 70,
          lower: 30,
          interval: '1h',
        },
        RENDER: {
          indicator: 'RSI',
          upper: 50,
          lower: 40,
          interval: '30m',
        },
        FET: {
          indicator: 'Commodity Channel Index',
          upper: 50,
          lower: 40,
          interval: '1h',
        },
        AVAX: {
          indicator: 'RSI',
          upper: 70,
          lower: 30,
          interval: '1h',
        },
      },
      coinList: [
        { id: 1, name: 'ETH' },
        { id: 2, name: 'BTC' },
        { id: 3, name: 'AVA' },
        { id: 4, name: 'SOL' },
        { id: 5, name: 'RENDER' },
        { id: 6, name: 'FET' },
        { id: 7, name: 'AVAX' },
      ],
      backtestCoins: ['ETH', 'BTC', 'AVA', 'SOL', 'RENDER', 'FET', 'AVAX'],
      coins: [],
      tradesByCoin: reactive<{ [key: string]: Trade[] }>({}),
      totalProfit: 0,
      finalBalance: 0,
      trades: [],
      indicators: [
        'RSI',
        'MACD',
        'Moving Average',
        'Exponential Moving Average',
        'Stochastic RSI',
        'Average Directional Index',
        'Volume Weighted Average Price',
        'Commodity Channel Index',
      ],
      indicatorValues: ref<{
        [key: string]: { upper: number; lower: number }
      }>({
        ETH: { upper: 70, lower: 30 },
        BTC: { upper: 60, lower: 40 },
        AVA: { upper: 70, lower: 30 },
        SOL: { upper: 70, lower: 30 },
        RENDER: { upper: 70, lower: 30 },
        FET: { upper: 70, lower: 30 },
        AVAX: { upper: 70, lower: 30 },
      }),
      intervalId: null as number | null,
      intervals: ['1m', '5m', '15m', '30m', '45m', '1h', '1d'],
    }
  },
  methods: {
    async handleFetchBacktest(params: Backtest) {
      console.log('Parameters ', params)
      try {
        const result = await fetchBacktest(params)
        this.finalBalance = result.finalBalance
        this.totalProfit = result.profit
        this.trades = result.trades
      } catch (error) {
        console.error('Backtest sorgusunda hata:', error)
      }
    },
    async fetchAllData() {
      try {
        const coins = await fetchCoins()
        this.coins = coins
        const tradesPromises = this.coinList.map(async (coin) => {
          const trades = await fetchTrades(coin.name)
          this.tradesByCoin[coin.name] = trades
        })
        await Promise.all(tradesPromises)
      } catch (error) {
        console.error('Veri çekme başarısız:', error)
        if (this.intervalId !== null) {
          clearInterval(this.intervalId)
          this.intervalId = null
        }
      }
    },
    startAll() {
      const controlBars = this.$refs.controlBars
      if (Array.isArray(controlBars)) {
        controlBars.forEach((controlBar) => controlBar?.start?.())
      }
    },
  },
  mounted() {
    this.fetchAllData()
    this.intervalId = setInterval(this.fetchAllData, 5000)
  },
  beforeUnmount() {
    if (this.intervalId !== null) {
      clearInterval(this.intervalId)
    }
  },
}
</script>

<style>
.container {
  padding: 20px;

  .coin-section {
    margin-bottom: 2rem;
  }

  .start-all {
    display: flex;
    justify-content: flex-end;
    align-items: center;
    gap: 20px;
    margin-top: 40px;
  }

  .text {
    font-size: 18px;
    color: #a9a9a9;
    font-weight: 600;
  }

  .startAll-button {
    background-color: #28a745;
    color: white;
    width: 180px;
    height: 45px;
    border-radius: 8px;
    border: 1px solid #28a745;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    transition:
      background-color 0.3s,
      transform 0.2s;
  }

  .start-button:hover {
    background-color: #218838;
    transform: scale(1.05);
  }

  .start-button:active {
    transform: scale(0.98);
  }
}
</style>
