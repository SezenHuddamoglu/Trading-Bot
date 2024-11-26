<template>
  <div class="input-c">
    <div class="input">
      <label class="input-label">{{ label }}</label>
      <input
        type="number"
        :value="modelValue"
        @input="$emit('update:modelValue', $event.target.value)"
        class="input-field"
      />
    </div>
  </div>
</template>

<script lang="ts">
export default {
  name: 'UIInput',
  props: {
    modelValue: {
      type: [String, Number], // String veya Number olabilir
      required: true,
    },
    label: {
      type: String,
      default: '',
    },
  },
}
</script>

<style scoped>
/* Input field styling */
.input-c {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.input-label {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.3rem;
  color: #d7d7d7;
}

.input-field {
  width: 100%;
  padding: 0.8rem 1.2rem;
  font-size: 1rem;
  border-radius: 8px;
  border: 1px solid #ccc;
  background-color: #f9f9f9;
  outline: none;
  transition: all 0.3s ease;
}

.input-field:focus {
  border-color: #007bff;
  background-color: #e6f1ff;
}

.input-field::placeholder {
  color: #aaa;
}

.input-field:hover {
  border-color: #007bff;
}
</style>
