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

    options: {
      type: Array as () => string[],
      required: true,
    },

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
.dropdown-container {
  display: flex;
  flex-direction: column;

  .dropdown-label {
    margin-bottom: 0.5rem;

    font-size: 14px;
    margin-right: 4px;
    color: aliceblue;
  }

  .dropdown-select {
    outline: none;
    transition: all 0.3s ease;
    width: 140px;
    background-color: #2c3338;
    color: aliceblue;
    border: 1px solid #444;
    border-radius: 4px;
    padding: 4px;
    font-size: 14px;
  }

  .dropdown select:focus {
    outline: none;
    border: 1px solid aliceblue;
  }

  .dropdown input {
    width: 100px;
    height: 30px;
    padding: 4px 8px;
    font-size: 14px;
    border: 1px solid #ccc;
    border-radius: 4px;
    background-color: #1b2126;
    color: aliceblue;
  }

  .dropdown-option {
    padding: 0.8rem;
    font-size: 1rem;
  }

  .dropdown-select:hover {
    border-color: #007bff;
  }
}
</style>
