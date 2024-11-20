<template>
  <div>
    <header>
      <h1>Coin Dashboard</h1>
    </header>
    <main>
      <slot />
      <!-- Sayfa içeriği buraya yüklenecek -->
    </main>
    <footer>
      <p>© 2024 Coin Dashboard</p>
    </footer>
  </div>
</template>
<script lang="ts">
export default {
  name: 'DefaultLayout',
}
</script>

<style scoped>
header {
  background-color: #282c34;
  color: white;
  padding: 1rem;
  text-align: center;
}
footer {
  background-color: #f8f9fa;
  text-align: center;
  padding: 1rem;
  position: fixed;
  bottom: 0;
  width: 100%;
}
main {
  padding: 2rem;
  margin-bottom: 60px; /* Footer için boşluk */
}
</style>
