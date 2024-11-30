<template>
  <div>
    <h2>Price Trend Chart</h2>
    <div ref="chartContainer" style="width: 100%; height: 500px"></div>
  </div>
</template>

<script lang="ts">
import { createChart, type IChartApi, type ISeriesApi, LineData, Time } from 'lightweight-charts'
import { Trade } from '../types/Trade'

export default {
  name: 'TradeChart',
  props: {
    trades: {
      type: Array as () => Trade[], // `trades`'in doğru türü belirtildi
      required: true,
    },
  },
  data() {
    return {
      chart: null as IChartApi | null,
      lineSeries: null as ISeriesApi<'Line'> | null,
    }
  },
  watch: {
    trades: {
      handler() {
        this.updateChart()
      },
      deep: true,
      immediate: true,
    },
  },
  mounted() {
    this.initializeChart()
  },
  methods: {
    initializeChart() {
      const container = this.$refs.chartContainer as HTMLDivElement
      this.chart = createChart(container, {
        width: container.clientWidth,
        height: container.clientHeight,
        layout: {
          background: '#fff', // Arka plan rengi için doğru kullanım
          textColor: '#d1d4dc',
        },
        crosshair: {
          vertLine: {
            visible: true,
            width: 1,
            color: '#FFFFFF',
            style: 1,
          },
          horzLine: {
            visible: true,
            width: 1,
            color: '#FFFFFF',
            style: 1,
          },
        },
        grid: {
          vertLines: {
            color: '#333333',
          },
          horzLines: {
            color: '#333333',
          },
        },
        timeScale: {
          timeVisible: true,
          secondsVisible: false,
        },
        priceScale: {
          borderColor: '#f0f0f0',
        },
        priceFormat: {
          type: 'custom',
          formatter: (price: number) => `$${price.toFixed(2)}`,
        },
      })

      this.lineSeries = this.chart.addLineSeries({
        color: 'navy',
        lineWidth: 2,
      })

      this.updateChart()
    },
    updateChart() {
      if (!this.lineSeries) return

      // `trade`'in türünü Trade olarak belirledik ve doğru türde zaman verisi kullandık
      const data: LineData<Time>[] = this.trades.map((trade) => ({
        time: Math.floor(new Date(trade.timestamp).getTime() / 1000) as Time, // `time` değerini doğru türde belirledik
        value: trade.price,
      }))

      this.lineSeries.setData(data)

      this.addMarkers()
    },
    addMarkers() {
      const markers = this.trades
        .map((trade) => {
          if (trade.action === 'buy') {
            return {
              time: Math.floor(new Date(trade.timestamp).getTime() / 1000) as Time, // `time`'ı doğru türde belirledik
              position: 'belowBar',
              color: 'green',
              shape: 'triangleUp',
              text: 'Buy',
            }
          } else if (trade.action === 'sell') {
            return {
              time: Math.floor(new Date(trade.timestamp).getTime() / 1000) as Time, // `time`'ı doğru türde belirledik
              position: 'aboveBar',
              color: 'red',
              shape: 'triangleDown',
              text: 'Sell',
            }
          }
          return null
        })
        .filter((marker) => marker !== null)

      this.lineSeries?.setMarkers(markers as any) // `setMarkers` için türü `any` olarak belirleyebiliriz çünkü `markers` dizisi karmaşık tip içeriyor
    },
  },
  beforeUnmount() {
    if (this.chart) {
      this.chart.remove()
    }
  },
}
</script>

<style scoped>
h2 {
  color: white;
  font-family: Arial, sans-serif;
  text-align: center;
}
</style>
