<template>
  <div>
    <h1>FastAPI + Vue.js Adder</h1>
    <div>
      <input type="number" v-model.number="num1" placeholder="Enter first number" />
      +
      <input type="number" v-model.number="num2" placeholder="Enter second number" />
    </div>
    <button @click="performAddition">Add Numbers</button>
    <hr>
    <div v-if="sum !== null">
      <h2>The Sum is: {{ sum }}</h2>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';

// Reactive variables
const num1 = ref(0);
const num2 = ref(0);
const sum = ref(null);
const apiUrl = 'http://127.0.0.1:8000/add'; // Matches your FastAPI server URL

async function performAddition() {
  // Clear previous sum
  sum.value = null;

  try {
    // Send a POST request to the FastAPI endpoint
    const response = await axios.post(apiUrl, {
      num1: num1.value,
      num2: num2.value
    });

    // Update the sum with the result from the backend
    sum.value = response.data.sum;
  } catch (error) {
    console.error("Error performing addition:", error);
    alert("Failed to connect to the backend or calculation error.");
  }
}
</script>

