<template>
  <DefaultLayout>
    <router-view />
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
  background-color: #06121e;
  font-family: 'Roboto', sans-serif;
}
</style>
