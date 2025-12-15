<script setup>
import { ref } from "vue";
import api from "@/api";
import DocumentPreviewModal from "@/views/Documents/DocumentPreviewModal.vue";

const query = ref("");
const results = ref([]);
const loading = ref(false);
const error = ref("");

const showPreview = ref(false);
const previewId = ref(null);

async function runSemanticSearch() {
  if (!query.value.trim()) return;

  loading.value = true;
  error.value = "";
  results.value = [];

  try {
    const res = await api.get("/documents/semantic-search", {
      params: { query: query.value }
    });
    results.value = res.data;
  } catch (err) {
    console.error(err);
    error.value = "Semantic search failed.";
  } finally {
    loading.value = false;
  }
}

function openPreview(id) {
  previewId.value = id;
  showPreview.value = true;
}
</script>

<template>
  <div class="p-8">
    <h1 class="text-2xl font-bold mb-4">Semantic Search</h1>

    <p class="text-gray-600 mb-4">
      Ask in natural language (e.g., “policy on procurement”, “faculty workload memo”).
    </p>

    <div class="flex gap-2 mb-6">
      <input
        v-model="query"
        @keyup.enter="runSemanticSearch"
        type="text"
        placeholder="Enter your question or topic..."
        class="flex-1 p-3 border rounded-lg focus:ring-2 focus:ring-green-500"
      />
      <button
        @click="runSemanticSearch"
        class="bg-green-700 text-white px-6 rounded-lg"
      >
        Search
      </button>
    </div>

    <div v-if="loading" class="text-gray-600">Searching...</div>
    <div v-if="error" class="text-red-600">{{ error }}</div>

    <table v-if="results.length" class="w-full bg-white shadow rounded-lg">
      <thead class="bg-green-700 text-white">
        <tr>
          <th class="p-3 text-left">Filename</th>
          <th class="p-3 text-left">Category</th>
          <th class="p-3 text-left">Uploader</th>
          <th class="p-3 text-left">Relevance</th>
          <th class="p-3 text-center">Action</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="doc in results"
          :key="doc.id"
          class="border-b hover:bg-gray-100"
        >
          <td class="p-3">{{ doc.filename }}</td>
          <td class="p-3">{{ doc.category }}</td>
          <td class="p-3">{{ doc.uploaded_by }}</td>
          <td class="p-3 font-mono text-sm">
            {{ doc.score }}
          </td>
          <td class="p-3 text-center">
            <button
              @click="openPreview(doc.id)"
              class="bg-blue-600 text-white px-4 py-2 rounded"
            >
              Preview
            </button>
          </td>
        </tr>
      </tbody>
    </table>

    <div v-if="!loading && results.length === 0 && query"
         class="text-gray-600 mt-6 text-center">
      No semantically similar documents found.
    </div>

    <DocumentPreviewModal
      :show="showPreview"
      :docId="previewId"
      @close="showPreview = false"
    />
  </div>
</template>
