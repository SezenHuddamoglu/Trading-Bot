<template>
  <div>
    <h2>Fiyat Trend Grafiği</h2>
    <canvas ref="chartCanvas"></canvas>
  </div>
</template>

<script lang="ts">
import {
  Chart,
  ChartConfiguration,
  LineController,
  LineElement,
  CategoryScale,
  LinearScale,
  Title,
  Tooltip,
  Legend,
  PointElement, // PointElement'i de dahil edin
} from 'chart.js' // Gerekli türleri içe aktar
import api from '../services/api'
import { Trade } from '../types/Trade'

export default {
  name: 'PriceChart',
  data() {
    return {
      trades: [] as Trade[], // trades dizisini data içinde tanımladık
      chartInstance: null as Chart | null, // chartInstance için null kontrolü
    }
  },
  methods: {
    async fetchTrades() {
      try {
        const response = await api.get('/trades')
        console.log('Gelen veri:', response.data)

        // `response.data.trades` dizisini alıyoruz
        this.trades = response.data.trades.map((trade: any) => ({
          action: trade.action,
          price: trade.price || 0,
          amount: trade.amount || 0,
          timestamp: trade.timestamp || '',
          indicator: trade.indicator || 'N/A',
        }))
      } catch (error) {
        console.error('İşlem geçmişi alınamadı:', error)
      }
    },

    formatDate(timestamp: number) {
      const date = new Date(timestamp)
      return date.toLocaleString()
    },

    createChart() {
      const chartCanvas = this.$refs.chartCanvas as HTMLCanvasElement
      if (chartCanvas) {
        if (this.chartInstance) {
          this.chartInstance.destroy() // Eski grafik varsa yok et
        }

        const config: ChartConfiguration<'line', number[], string> = {
          type: 'line',
          data: {
            labels: this.trades.map((trade) => this.formatDate(trade.timestamp)),
            datasets: [
              {
                label: 'Fiyat',
                data: this.trades.map((trade) => trade.price),
                fill: false,
                borderColor: 'blue',
              },
            ],
          },
          options: {
            responsive: true,
            plugins: {
              legend: {
                position: 'top',
              },
            },
          },
        }

        this.chartInstance = new Chart(chartCanvas, config)
      }
    },
  },
  mounted() {
    this.fetchTrades()
    setInterval(this.fetchTrades, 5000) // 5 saniyede bir verileri güncelle
    Chart.register(
      LineController,
      LineElement,
      CategoryScale,
      LinearScale,
      Title,
      Tooltip,
      Legend,
      PointElement,
    )
    this.createChart()
  },
}
</script>

<style scoped>
canvas {
  width: 100% !important;
  height: 400px !important;
}
</style>
