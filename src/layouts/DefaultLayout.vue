<template>
  <div>
    <header>
      <div class="header-content">
        <h1>Coin Dashboard</h1>
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
  /* background-color: #06121e; */
  background-color: #0B192C;
  color: whitesmoke;
  text-align: center;
  padding: 1rem;
  position: fixed;
  bottom: 0;
  width: 100%;
}
main {
  background-color:#0B192C;
  padding: 2rem;
  margin-bottom: 60px; /* Footer için boşluk */
}
</style>
