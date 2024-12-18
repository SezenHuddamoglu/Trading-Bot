<template>
  <div class="input-c">
    <label class="input-label">{{ label }}</label>
    <input type="number" :value="modelValue" @input="handleInput" class="input-field" />
  </div>
</template>

<script lang="ts">
export default {
  name: 'UIInput',
  props: {
    modelValue: {
      type: [String, Number],
      required: true,
    },
    label: {
      type: String,
      default: '',
    },
  },
  methods: {
    handleInput(event: Event) {
      const input = event.target as HTMLInputElement
      if (input) {
        this.$emit('update:modelValue', input.value)
      }
    },
  },
}
</script>

<style scoped>
.input-c {
  display: flex;
  flex-direction: column;

  .input-label {
    margin-bottom: 0.3rem;
    font-size: 14px;
    margin-right: 4px;
    color: aliceblue;
  }

  .input-field {
    width: 100px;
    font-size: 1rem;
    outline: none;
    transition: all 0.3s ease;

    background-color: #2c3338;
    color: aliceblue;
    border: 1px solid #444;
    border-radius: 4px;
    padding: 4px;
    font-size: 12px;
  }

  .input-field :focus {
    outline: none;
    border: 1px solid aliceblue;
  }

  .input-field::placeholder {
    color: #aaa;
  }

  .input-field:hover {
    border-color: #007bff;
  }
}
</style>
