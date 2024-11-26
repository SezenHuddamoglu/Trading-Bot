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
      type: Array,
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
/* Dropdown Container */
.dropdown-container {
  display: flex;
  flex-direction: column;
  margin-bottom: 1rem;
}

/* Label Styling */
.dropdown-label {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #d7d7d7;
}

/* Select Box Styling */
.dropdown-select {
  padding: 0.8rem 1rem;
  font-size: 1rem;
  border-radius: 8px;
  border: 1px solid #ccc;
  background-color: #f9f9f9;
  outline: none;
  transition: all 0.3s ease;
}

.dropdown-select:focus {
  border-color: #007bff;
  background-color: #e6f1ff;
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
</style>
