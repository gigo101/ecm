<script setup>
import { ref, onMounted } from "vue"
import api from "@/api"
import { useRouter } from "vue-router"

const documents = ref([])
const loading = ref(true)
const router = useRouter()

async function fetchSharedDocs() {
  try {
    const res = await api.get("/documents/shared-with-me")

    // show only top 5
    documents.value = res.data.slice(0, 5)

  } finally {
    loading.value = false
  }
}

onMounted(fetchSharedDocs)
</script>

<template>
  <div class="bg-white shadow rounded-lg p-5">

    <h2 class="text-lg font-semibold mb-3 text-dns_dark">
      📄 Shared With You
    </h2>

    <div v-if="loading" class="text-sm text-gray-500">
      Loading...
    </div>

    <div v-else>

      <p
        v-if="documents.length"
        class="text-sm text-gray-600 mb-2"
      >
        You have {{ documents.length }} shared document(s)
      </p>

      <ul class="text-sm space-y-1">
        <li
          v-for="doc in documents"
          :key="doc.id"
          class="hover:text-green-700 cursor-pointer"
          @click="router.push('/documents/shared')"
        >
          • {{ doc.filename }}
        </li>
      </ul>

      <p
        v-if="documents.length === 0"
        class="text-sm text-gray-500"
      >
        No documents shared with you.
      </p>

      <button
        v-if="documents.length"
        @click="router.push('/documents/shared')"
        class="mt-3 text-xs text-green-700 hover:underline"
      >
        View All
      </button>

    </div>

  </div>
</template>