<script setup>
import { ref } from "vue";
import api from "@/api";
import DocumentPreviewModal from "@/views/Documents/DocumentPreviewModal.vue";

const query = ref("");
const results = ref([]);
const loading = ref(false);
const error = ref("");
const previewQuery = ref("");
const showPreview = ref(false);
const previewId = ref(null);
const highlights = ref([]);
const previewSource = ref("SEMANTIC_SEARCH"); // 👈 ADD
const yearFrom = ref(null);
const yearTo = ref(null);
const role = ref(localStorage.getItem("role"));


const category = ref("");

const categories = [
  "General",
  "Administrative",
  "Academics",
  "Research",
  "Policies",
  "Official Issuances",
  "News & Events"
];


const props = defineProps({
  show: Boolean,
  docId: Number,
  query: String,
});


const currentYear = new Date().getFullYear();

const years = Array.from(
  { length: currentYear - 2010 },
  (_, i) => currentYear - i
);


async function runSemanticSearch() {

  if (yearFrom.value && yearTo.value && yearFrom.value > yearTo.value) {
    error.value = "From year cannot be later than To year.";
    return;
  }

  if (!query.value.trim()) return;

  loading.value = true;
  error.value = "";
  results.value = [];

  try {
    const params = { query: query.value };

    if (yearFrom.value) params.year_from = Number(yearFrom.value);
    if (yearTo.value) params.year_to = Number(yearTo.value);

    if (category.value && category.value !== "") {
      params.category = category.value;
    }

    const res = await api.get("/documents/semantic-search", { params });

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
  previewQuery.value = query.value; // ← pass search query
  previewSource.value = "SEMANTIC_SEARCH"; // 👈 ADD
  showPreview.value = true;
}

function downloadFile(filename) {
  if (!metadata.value.filename) return;
  window.open(`http://127.0.0.1:8000/uploads/${filename}`, "_blank");
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

      <select
        v-model="yearFrom"
        class="p-3 border rounded-lg w-40 focus:ring-2 focus:ring-green-500"
      >
        <option :value="null">From year</option>
        <option
          v-for="y in years"
          :key="'from-' + y"
          :value="y"
        >
          {{ y }}
        </option>
      </select>

      <select
        v-model="yearTo"
        class="p-3 border rounded-lg w-40 focus:ring-2 focus:ring-green-500"
      >
        <option :value="null">To year</option>
        <option
          v-for="y in years"
          :key="'to-' + y"
          :value="y"
        >
          {{ y }}
        </option>
      </select>

      <select v-model="category" class="p-3 border rounded-lg w-52 focus:ring-2 focus:ring-green-500"
    >
      <option value="">All Categories</option>

      <option
        v-for="c in categories"
        :key="c"
        :value="c"
      >
        {{ c }}
      </option>
      </select>

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
      :query="previewQuery"
      :source="previewSource"
      @close="showPreview = false"
    />
  </div>
</template>
