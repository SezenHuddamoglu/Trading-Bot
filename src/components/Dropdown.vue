<template>
  <div class="dropdown-container">
    <label :for="id" class="dropdown-label">{{ label }}:</label>
    <select v-model="selectedValue" :id="id" class="dropdown-select">
      <option v-for="option in options" :key="option" :value="option" class="dropdown-option">
        {{ option }}
      </option>
    </select>
  </div>
</template>

<script lang="ts">
export default {
  name: 'UIDropdown',
  props: {
    id: {
      type: String,
      required: true,
    },
    label: {
      type: String,
      required: true,
    },
    // options array tipini string[] olarak belirtiyoruz
    options: {
      type: Array as () => string[], // Burada dizi tipi belirtildi
      required: true,
    },
    // modelValue için tip belirtiyoruz
    modelValue: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      selectedValue: this.modelValue,
    }
  },
  watch: {
    selectedValue(newValue) {
      this.$emit('update:modelValue', newValue)
    },
  },
}
</script>

<style scoped>
/* Dropdown Container */
.dropdown-container {
  display: flex;
  flex-direction: column;

  /* Label Styling */
  .dropdown-label {
    margin-bottom: 0.5rem;

    font-size: 14px;
    margin-right: 4px;
    color: aliceblue;
  }

  /* Select Box Styling */
  .dropdown-select {
    outline: none;
    transition: all 0.3s ease;
    width: 140px;
    background-color: #2c3338; /* Gri bir arka plan rengi */
    color: aliceblue; /* Beyaz yazı rengi */
    border: 1px solid #444; /* Gri kenarlık */
    border-radius: 4px; /* Hafif yuvarlatılmış kenarlar */
    padding: 4px; /* İçerik ile kenar boşluğu */
    font-size: 14px; /* Yazı boyutunu küçült */
  }

  .dropdown select:focus {
    outline: none; /* Odaklandığında varsayılan çerçeve kaldırılır */
    border: 1px solid aliceblue; /* Odaklandığında kenarlık beyaz olur */
  }

  .dropdown input {
    width: 100px; /* Genişliği azaltarak daha ince görünmesini sağlayın */
    height: 30px; /* Yüksekliği azaltın */
    padding: 4px 8px; /* İçerik ile kenar arasındaki boşluğu küçültün */
    font-size: 14px; /* Yazı boyutunu küçültün */
    border: 1px solid #ccc; /* İnce bir kenarlık ekleyin */
    border-radius: 4px; /* Hafif yuvarlatılmış köşeler */
    background-color: #1b2126; /* Arka plan rengini aynı temaya uygun hale getirin */
    color: aliceblue;
  }
  /* Option Styling */
  .dropdown-option {
    padding: 0.8rem;
    font-size: 1rem;
  }

  /* Hover effect for options */
  .dropdown-select:hover {
    border-color: #007bff;
  }
}
</style>
