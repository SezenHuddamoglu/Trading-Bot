<template>
  <div>
    <h2>Price Trend Chart</h2>
    <div ref="chartContainer" style="width: 100%; height: 500px"></div>
  </div>
</template>

<script lang="ts">
import { createChart } from 'lightweight-charts'

export default {
  name: 'TradeChart',
  props: {
    trades: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      chart: null,
      lineSeries: null,
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
      // Chart'ı başlat
      const container = this.$refs.chartContainer
      this.chart = createChart(container, {
        width: container.clientWidth,
        height: container.clientHeight,
        backgroundColor: 'black', // Grafik arkaplanını siyah yap
        crosshair: {
          vertLine: {
            visible: true,
            width: 1,
            color: '#FFFFFF', // Çizgilerin rengini beyaz yap
            style: 1,
          },
          horzLine: {
            visible: true,
            width: 1,
            color: '#FFFFFF', // Çizgilerin rengini beyaz yap
            style: 1,
          },
        },
        grid: {
          vertLines: {
            color: '#333333', // Kılavuz çizgilerinin rengini gri yap
          },
          horzLines: {
            color: '#333333', // Kılavuz çizgilerinin rengini gri yap
          },
        },
        timeScale: {
          timeVisible: true,
          secondsVisible: false,
        },
        priceScale: {
          borderColor: '#f0f0f0', // Fiyat ölçeği sınırını beyaz yap
        },
      })

      // LineSeries ekle
      this.lineSeries = this.chart.addLineSeries({
        color: 'navy', // Eğri rengini lacivert yap
        lineWidth: 2,
      })

      // Başlangıçta grafiği güncelle
      this.updateChart()
    },
    updateChart() {
      if (!this.lineSeries) return

      // Verileri TradingView formatına dönüştür
      const data = this.trades.map((trade) => ({
        time: Math.floor(new Date(trade.timestamp).getTime() / 1000), // Timestamp'i saniyeye dönüştür
        value: trade.price, // Fiyat
      }))

      // LineSeries'i güncelle
      this.lineSeries.setData(data)

      // Buy ve Sell işaretlerini ekle
      this.addMarkers()
    },
    addMarkers() {
      // Buy ve Sell noktaları eklemek için örnek veriler
      const markers = this.trades
        .map((trade) => {
          let marker = null
          if (trade.action === 'buy') {
            marker = {
              time: Math.floor(new Date(trade.timestamp).getTime() / 1000),
              position: 'belowBar',
              color: 'green', // Buy işareti için yeşil renk
              shape: 'triangleUp', // Yukarı üçgen
              text: 'Buy',
            }
          } else if (trade.action === 'sell') {
            marker = {
              time: Math.floor(new Date(trade.timestamp).getTime() / 1000),
              position: 'aboveBar',
              color: 'red', // Sell işareti için kırmızı renk
              shape: 'triangleDown', // Aşağı üçgen
              text: 'Sell',
            }
          }
          return marker
        })
        .filter((marker) => marker !== null)

      // Add markers to chart manually using addSeries
      markers.forEach((marker) => {
        this.chart.addMarker({
          time: marker.time,
          position: marker.position,
          color: marker.color,
          shape: marker.shape,
          text: marker.text,
        })
      })
    },
  },
  beforeUnmount() {
    // Chart örneğini yok et
    if (this.chart) {
      this.chart.remove()
    }
  },
}
</script>

<style scoped>
h2 {
  color: white; /* Başlık rengini beyaz yap */
  font-family: Arial, sans-serif;
  text-align: center;
}
</style>
