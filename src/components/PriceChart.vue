<template>
  <div>
    <h2>Price Trend Chart</h2>
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
  //ChartTypeRegistry,
} from 'chart.js' // Gerekli türleri içe aktar

import { Trade } from '../types/Trade'

// Trade tipi

export default {
  name: 'PriceChart',
  props: {
    trades: {
      type: Array as () => Trade[],
      required: true,
    },
  },
  data() {
    return {
      chartInstance: null as Chart<'line', number[], string> | null,
    }
  },
  methods: {
    createChart() {
      const canvas = this.$refs.chartCanvas as HTMLCanvasElement
      if (!canvas) return
      // Eski grafik varsa yok et
      if (this.chartInstance) {
        this.chartInstance.destroy()
      }
      // Grafik yapılandırması
      const config: ChartConfiguration<'line', number[], string> = {
        type: 'line',
        data: {
          labels: this.trades.map((trade) => new Date(trade.timestamp).toLocaleString()),
          datasets: [
            {
              label: 'Fiyat',
              data: this.trades.map((trade) => trade.price),
              borderColor: 'blue',
              fill: false,
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            legend: { position: 'top' },
          },
        },
      }
      // Yeni Chart.js örneği oluştur
      this.chartInstance = new Chart(canvas, config)
    },
  },
  watch: {
    trades: {
      handler() {
        this.createChart() // trades değiştiğinde grafiği güncelle
      },
      deep: true,
      immediate: true,
    },
  },
  mounted() {
    // Chart.js bileşenlerini kaydet
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
    this.createChart() // İlk grafik oluştur
  },
  beforeUnmount() {
    // Grafik örneğini yok et
    if (this.chartInstance) {
      this.chartInstance.destroy()
    }
  },
}
</script>

<style scoped>
canvas {
  width: 100% !important;
  height: 400px !important;
}
h2 {
  color: #f2f2f2;
}
</style>
