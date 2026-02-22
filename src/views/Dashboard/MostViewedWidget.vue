<script setup>
import { ref, onMounted } from "vue"
import api from "@/api"

const docs = ref([])
const loading = ref(true)

async function loadMostViewed() {
  try {
    const res = await api.get("/dashboard/most-viewed")
    docs.value = res.data
  } finally {
    loading.value = false
  }
}

onMounted(loadMostViewed)
</script>

<template>
  <div class="bg-white p-6 rounded shadow">

    <div class="text-sm text-gray-500 mb-3">
      🔥 Most Viewed Documents
    </div>

    <div v-if="loading" class="text-sm text-gray-400">
      Loading...
    </div>

    <ul v-else class="space-y-2 text-sm">

      <li
        v-for="(doc, index) in docs"
        :key="doc.id"
        class="flex justify-between"
      >
        <span>
          {{ index + 1 }}. {{ doc.title }}
        </span>

        <span class="text-gray-500">
          {{ doc.views }} views
        </span>
      </li>

      <li v-if="docs.length === 0" class="text-gray-500">
        No view data yet.
      </li>

    </ul>

  </div>
</template>