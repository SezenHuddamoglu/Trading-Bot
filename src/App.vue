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
</script>

<style>
body {
  font-family: 'Roboto', sans-serif; /* İstediğiniz fontu buraya ekleyin */
}
</style>
