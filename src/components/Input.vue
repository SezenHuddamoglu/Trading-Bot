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
/* Input field styling */
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

    background-color: #2c3338; /* Gri bir arka plan rengi */
    color: aliceblue; /* Beyaz yazı rengi */
    border: 1px solid #444; /* Gri kenarlık */
    border-radius: 4px; /* Hafif yuvarlatılmış kenarlar */
    padding: 4px; /* İçerik ile kenar boşluğu */
    font-size: 12px; /* Yazı boyutunu küçült */
  }

  .input-field :focus {
    outline: none; /* Odaklandığında varsayılan çerçeve kaldırılır */
    border: 1px solid aliceblue; /* Odaklandığında kenarlık beyaz olur */
  }

  .input-field::placeholder {
    color: #aaa;
  }

  .input-field:hover {
    border-color: #007bff;
  }
}
</style>
