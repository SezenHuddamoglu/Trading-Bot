<template>
  <div>
    <h2>Price Trend Chart</h2>
    <div ref="chartContainer" style="width: 100%; height: 500px; position: relative">
      <div
        id="tooltip"
        style="
          display: none;
          position: absolute;
          background: rgba(0, 0, 0, 0.75);
          color: #fff;
          padding: 5px;
          border-radius: 3px;
          pointer-events: none;
        "
      ></div>
    </div>
  </div>
</template>

<script lang="ts">
import { createChart, type IChartApi, type ISeriesApi, LineData, Time } from 'lightweight-charts'
import { Trade } from '../types/Trade'
import { MouseEventParams } from 'lightweight-charts'
export default {
  name: 'TradeChart',
  props: {
    trades: {
      type: Array as () => Trade[],
      required: true,
    },
  },
  data() {
    return {
      chart: null as IChartApi | null,
      lineSeries: null as ISeriesApi<'Line'> | null,
      buySeries: null as ISeriesApi<'Line'> | null,
      sellSeries: null as ISeriesApi<'Line'> | null,
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
    this.$nextTick(() => {
      this.initializeChart()
    })
  },
  methods: {
    initializeChart() {
      const container = this.$refs.chartContainer as HTMLDivElement
      this.chart = createChart(container, {
        width: container.clientWidth,
        height: container.clientHeight,
        layout: {
          background: '#f9f9f9',
          textColor: '#333',
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
        color: 'blue',
        lineWidth: 2,
      })
      // Buy series
      this.buySeries = this.chart.addLineSeries({
        color: '#6abf69', // Lighter green
        lineWidth: 2,
        lineStyle: 2,
        title: 'Buy',
      })

      // Sell series
      this.sellSeries = this.chart.addLineSeries({
        color: '#ff6b6b', // Pastel red
        lineWidth: 2,
        lineStyle: 2, // Dashed line
        title: 'Sell',
      })

      this.addMarkers()
      this.addTooltip()
      this.updateChart()
    },
    updateChart() {
      if (!this.lineSeries) return

      const data: LineData<Time>[] = this.trades.map((trade) => ({
        time: Math.floor(new Date(trade.timestamp).getTime() / 1000) as Time,
        value: trade.price,
      }))

      this.lineSeries.setData(data)

      if (!this.buySeries || !this.sellSeries) return

      const buyData: LineData<Time>[] = this.trades
        .filter((trade) => trade.action.toLowerCase() === 'buy')
        .map((trade) => ({
          time: Math.floor(new Date(trade.timestamp).getTime() / 1000) as Time,
          value: trade.price,
        }))

      const sellData: LineData<Time>[] = this.trades
        .filter((trade) => trade.action.toLowerCase() === 'sell')
        .map((trade) => ({
          time: Math.floor(new Date(trade.timestamp).getTime() / 1000) as Time,
          value: trade.price,
        }))

      this.buySeries.setData(buyData)
      this.sellSeries.setData(sellData)
      this.addMarkers()
      this.addTooltip()
    },
    addMarkers() {
      if (!this.buySeries || !this.sellSeries) return

      this.buySeries.setMarkers(
        this.trades
          .filter((trade) => trade.action.toLowerCase() === 'buy')
          .map((trade) => ({
            time: Math.floor(new Date(trade.timestamp).getTime() / 1000) as Time,
            position: 'aboveBar',
            color: 'green',
            shape: 'arrowUp',
            size: 0.4,
          })),
      )

      this.sellSeries.setMarkers(
        this.trades
          .filter((trade) => trade.action.toLowerCase() === 'sell')
          .map((trade) => ({
            time: Math.floor(new Date(trade.timestamp).getTime() / 1000) as Time,
            position: 'belowBar',
            color: 'red',
            shape: 'arrowDown',
            size: 0.4,
          })),
      )
    },
    addTooltip() {
      if (!this.chart) return

      this.chart.subscribeCrosshairMove((param: MouseEventParams<Time>) => {
        // Ensure the type is MouseEventParams
        const tooltip = document.getElementById('tooltip')
        if (!tooltip) return

        // Ensure we have valid seriesPrices, and the series are added correctly
        if (!param.time || !param.seriesData) {
          tooltip.style.display = 'none'
          return
        }

        const buyPrice = param.seriesData.get(this.buySeries! as ISeriesApi<'Line'>) // Use type assertion
        const sellPrice = param.seriesData.get(this.sellSeries! as ISeriesApi<'Line'>)

        tooltip.style.display = 'block'
        tooltip.style.left = `${param.point?.x}px`
        tooltip.style.top = `${param.point?.y}px`
        tooltip.innerHTML = `
      ${buyPrice ? `<div>Buy Price: ${buyPrice}</div>` : ''}
      ${sellPrice ? `<div>Sell Price: ${sellPrice}</div>` : ''}
    `
      })
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
  color: #333;
  font-family: Arial, sans-serif;
  text-align: center;
  margin-bottom: 10px;
}
</style>
