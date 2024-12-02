<!-- <script setup lang="ts">
import { RouterView } from 'vue-router' //RouterLink,
</script>

<template>
  <RouterView />
</template>

<style scoped></style> -->
<!-- src/App.vue -->
<template>
  <DefaultLayout>
    <router-view />
    <!-- Sayfa içeriği burada yüklenecek -->
  </DefaultLayout>
</template>

<script lang="ts">
import DefaultLayout from './layouts/DefaultLayout.vue'

export default {
  name: 'App',
  components: { DefaultLayout },
}

// async function testApi() {
//   try {
//     const params = {
//       coin: 'ETH', // Örnek değerler
//       indicator: 'MACD',
//       upper: 60,
//       lower: 40,
//       balance: 10000,
//       interval: '1h',
//     }

//     const response = await api.post('/api/backtest', params)
//     console.log('API testi başarılı:', response.data)
//   } catch (error) {
//     if (error.response) {
//       // Backend'den dönen hata yanıtını gösterir
//       console.error('API Hata Yanıtı:', error.response.data)
//     } else {
//       console.error('API testi başarısız:', error)
//     }
//   }
// }

// testApi()
</script>

<style>
body {
  background-color: #06121e;
  font-family: 'Roboto', sans-serif; /* İstediğiniz fontu buraya ekleyin */
}
</style>
