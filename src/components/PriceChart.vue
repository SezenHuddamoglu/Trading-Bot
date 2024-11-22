<template>
  <div>
    <h2>Fiyat Trend Grafiği</h2>
    <canvas ref="chartCanvas"></canvas>
  </div>
</template>

<script lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
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
  //ChartTypeRegistry,
} from 'chart.js' // Gerekli türleri içe aktar

import api from '../services/api'
import { Trade } from '../types/Trade'

// Trade tipi

export default {
  name: 'PriceChart',
  setup() {
    const trades = ref<Trade[]>([]) // trades tipini belirledik
    const chartCanvas = ref<HTMLCanvasElement | null>(null) // chartCanvas için null kontrolü
    let chartInstance: Chart | null = null // chartInstance için doğru tip belirtildi

    // Trades verisini almak için fetchTrades fonksiyonu
    const fetchTrades = async () => {
      try {
        const response = await api.get('/trades')
        console.log('Gelen veri:', response.data)

        // `response.data.trades` dizisini alıyoruz
        trades.value = response.data.trades.map((trade: any) => ({
          action: trade.action,
          price: trade.price || 0,
          amount: trade.amount || 0,
          timestamp: trade.timestamp || '',
          indicator: trade.indicator || 'N/A', // Varsayılan değer ekleyebilirsiniz
        }))
      } catch (error) {
        console.error('İşlem geçmişi alınamadı:', error)
      }
    }

    // Date formatı
    const formatDate = (timestamp: number) => {
      const date = new Date(timestamp)
      return date.toLocaleString()
    }

    // Grafik oluşturma fonksiyonu
    const createChart = () => {
      if (chartCanvas.value) {
        if (chartInstance) {
          chartInstance.destroy()
        }

        const config: ChartConfiguration<'line', number[], string> = {
          type: 'line',
          data: {
            labels: trades.value.map((trade) => formatDate(trade.timestamp)),
            datasets: [
              {
                label: 'Fiyat',
                data: trades.value.map((trade) => trade.price),
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

        chartInstance = new Chart(chartCanvas.value, config)
      }
    }

    let intervalId: number | null = null

    onMounted(() => {
      fetchTrades()
      intervalId = setInterval(fetchTrades, 5000)
    })

    onUnmounted(() => {
      if (intervalId !== null) {
        clearInterval(intervalId)
      }
    })
    // Grafik oluşturulması
    onMounted(() => {
      // Chart.js bileşenlerini kaydedin
      Chart.register(
        LineController,
        LineElement,
        CategoryScale,
        LinearScale,
        Title,
        Tooltip,
        Legend,
        PointElement, // PointElement'i de kaydediyoruz
      )
      createChart()
    })

    return { trades, formatDate, chartCanvas }
  },
}
</script>

<style scoped>
canvas {
  width: 100% !important;
  height: 400px !important;
}
</style>
