<template>
  <div>
    <header>
      <div class="header-content">
        <div class="logos">
          <div class="logo logo1"></div>
          <img :src="`./src/assets/BNB-arma.png`" />
          <img src="./src/assets/SOL-arma.png" alt="Logo 2" />
          <img src="./src/assets/DOGE-arma.png" alt="Logo 3" />
        </div>
        <h1>Coin Dashboard</h1>
        <div class="logos">
          <img src="./src/assets/BTC-arma.png" alt="Logo 4" />
          <img src="./src/assets/ETH-arma.png" alt="Logo 5" />
          <img src="./src/assets/XRP-arma.png" alt="Logo 6" />
        </div>

      </div>

    </header>
    <main>
      <slot/>
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

/* Sol ve sağdaki logolar için düzen */
.logos {
  display: flex;
  gap: 10px; /* Logolar arasında boşluk */
}

/* Logo resimlerinin boyut ayarları */
.logos img {
  height: 40px; /* Resim yüksekliği */
  width: auto;
}
h1 {
  flex-grow: 1;
  text-align: center;
  margin: 0;
}

footer {
  background-color: #06121e;
  color: whitesmoke;
  text-align: center;
  padding: 1rem;
  position: fixed;
  bottom: 0;
  width: 100%;
}
main {
  background-color:#06121e;
  padding: 2rem;
  margin-bottom: 60px; /* Footer için boşluk */
}
</style>
