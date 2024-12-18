<template>
  <div>
    <header>
      <div class="header-content">
        <h1>Coin Dashboard</h1>
      </div>
    </header>
    <main>
      <slot />
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
  background-color: #6c717a;
  color: #06121e;
  padding: 1rem;
  text-align: center;
}
.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.logos {
  display: flex;
  gap: 10px;
}

.logos img {
  height: 40px;
  width: auto;
}
h1 {
  flex-grow: 1;
  text-align: center;
  margin: 0;
}

footer {
  background-color: #0b192c;
  color: whitesmoke;
  text-align: center;
  padding: 1rem;
  position: fixed;
  bottom: 0;
  width: 100%;
}
main {
  background-color: #0b192c;
  padding: 2rem;
  margin-bottom: 60px;
}
</style>
