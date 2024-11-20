<template>
  <div>
    <h2>Fiyat Trend Grafiği</h2>
    <canvas ref="chartCanvas"></canvas>
  </div>
</template>

<script lang="ts">
import { ref, onMounted } from 'vue'
import { Chart, ChartConfiguration, ChartTypeRegistry } from 'chart.js' // Import necessary types
import api from '../services/api'

// Trade tipi
interface Trade {
  timestamp: number
  price: number
  action: string
  amount: number
  indicator: string
}

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
        trades.value = response.data
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
        const config: ChartConfiguration<keyof ChartTypeRegistry, number[], string> = {
          type: 'line', // 'line' is valid as per ChartTypeRegistry
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

        // Eski chart varsa önceki grafiği yok et
        if (chartInstance) {
          chartInstance.destroy()
        }

        // Yeni chart oluştur
        chartInstance = new Chart(chartCanvas.value, config)
      }
    }

    // Veriyi düzenli aralıklarla güncelle
    onMounted(() => {
      fetchTrades()
      setInterval(() => {
        fetchTrades()
      }, 5000) // 5 saniyede bir güncelle
    })

    // Grafik oluşturulması
    onMounted(createChart)

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
