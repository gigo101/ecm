<script setup>
import { ref } from 'vue'
const query = ref('')
const results = ref([])

async function search() {
// placeholder: call your backend search API
results.value = [
{ id: 1, title: 'Student Handbook.pdf', snippet: 'Guidelines on conduct, ...', score: 0.92 }
]
}
</script>

<template>
<div>
<h1 class="text-xl font-semibold text-dns_dark mb-4">Smart Search</h1>
<div class="flex gap-3 mb-4">
<input v-model="query" @keyup.enter="search" class="flex-1 border p-2 rounded" placeholder="Search documents..." />
<button @click="search" class="px-4 py-2 bg-dns_dark text-white rounded">Search</button>
</div>

<div v-if="results.length" class="space-y-4">
<div v-for="r in results" :key="r.id" class="bg-white p-4 rounded shadow">
<div class="flex justify-between items-start">
<div>
<div class="font-semibold">{{ r.title }}</div>
<div class="text-sm text-gray-600">{{ r.snippet }}</div>
</div>
<div class="text-sm text-gray-500">Score: {{ r.score }}</div>
</div>
</div>
</div>
</div>
</template>


