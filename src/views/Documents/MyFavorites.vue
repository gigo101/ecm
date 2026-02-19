<script setup>
import { ref, onMounted, computed } from "vue"
import api from "@/api"
import DocumentPreviewModal from "@/views/Documents/DocumentPreviewModal.vue"
import { useToast } from "vue-toastification"

const documents = ref([])
const loading = ref(true)
const error = ref("")
const toast = useToast()

const showPreview = ref(false)
const previewId = ref(null)

const search = ref("")
const category = ref("")

const categories = [
  "Administrative",
  "Academics",
  "Research",
  "Policies",
  "Official Issuances",
  "News & Events",
  "General"
]

const filteredDocuments = computed(() => {
  return documents.value.filter(doc => {
    const matchCategory =
      !category.value || doc.category === category.value

    const matchSearch =
      !search.value ||
      doc.filename.toLowerCase().includes(search.value.toLowerCase())

    return matchCategory && matchSearch
  })
})

async function fetchFavorites() {
  loading.value = true
  error.value = ""

  try {
    const res = await api.get("/documents/my-favorites")
    documents.value = res.data
  } catch (err) {
    console.error(err)
    error.value = "Failed to load favorites."
  } finally {
    loading.value = false
  }
}

function openPreview(id) {
  previewId.value = id
  showPreview.value = true
}

async function toggleFavorite(doc) {
  try {
    const res = await api.post(`/documents/${doc.id}/favorite`)

    if (res.data.status === "removed") {
      documents.value = documents.value.filter(d => d.id !== doc.id)
      toast.success("Removed from favorites")
    }
  } catch (err) {
    console.error(err)
    toast.error("Action failed")
  }
}

onMounted(fetchFavorites)
</script>

<template>
  <div class="p-8">
    <h1 class="text-2xl font-bold mb-6">My Favorites</h1>

    <div v-if="loading">Loading...</div>
    <div v-if="error" class="text-red-600">{{ error }}</div>

    <!-- 🔎 FILTER BAR -->
    <div class="flex flex-col md:flex-row gap-3 mb-4">

      <!-- SEARCH -->
      <div class="relative w-full md:max-w-md">
        <input
          v-model="search"
          type="text"
          placeholder="Search favorites..."
          class="w-full p-3 pl-10 border rounded-lg focus:ring-2 focus:ring-green-500"
        />

        <svg
          class="absolute left-3 top-3.5 h-5 w-5 text-gray-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M21 21l-4.35-4.35M11 19a8 8 0 100-16 8 8 0 000 16z"/>
        </svg>
      </div>

      <!-- CATEGORY -->
      <select
        v-model="category"
        class="p-3 border rounded-lg w-full md:w-64 focus:ring-2 focus:ring-green-500"
      >
        <option value="">All Categories</option>
        <option v-for="c in categories" :key="c" :value="c">
          {{ c }}
        </option>
      </select>
    </div>

    <!-- RESULT COUNT -->
    <p class="text-sm text-gray-600 mb-2">
      Showing {{ filteredDocuments.length }} result(s)
    </p>

    <!-- TABLE -->
    <table
      v-if="filteredDocuments.length"
      class="w-full bg-white shadow rounded-lg"
    >
      <thead class="bg-green-700 text-white">
        <tr>
          <th class="p-3 text-left">Filename</th>
          <th class="p-3 text-left">Category</th>
          <th class="p-3 text-left">Type</th>
          <th class="p-3 text-left">Year</th>
          <th class="p-3 text-left">Uploaded By</th>
          <th class="p-3 text-left">Date</th>
          <th class="p-3 text-center">Preview</th>
          <th class="p-3 text-center">Favorite</th>
        </tr>
      </thead>

      <tbody>
        <tr
          v-for="doc in filteredDocuments"
          :key="doc.id"
          class="border-b hover:bg-gray-100"
        >
          <td class="p-3">{{ doc.filename }}</td>
          <td class="p-3">{{ doc.category }}</td>
          <td class="p-3">{{ doc.document_type }}</td>
          <td class="p-3">{{ doc.year_approved }}</td>
          <td class="p-3">{{ doc.uploaded_by }}</td>
          <td class="p-3">{{ doc.uploaded_at }}</td>

          <td class="p-3 text-center">
            <button
              @click="openPreview(doc.id)"
              class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
            >
              Preview
            </button>
          </td>

          <td class="p-3 text-center">
            <button
              @click="toggleFavorite(doc)"
              class="text-yellow-500 text-2xl hover:scale-110 transition"
              title="Remove from favorites"
            >
              ⭐
            </button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- EMPTY STATE -->
    <div
      v-if="!loading && filteredDocuments.length === 0"
      class="text-gray-600 mt-6 text-center"
    >
      No favorite documents found.
    </div>
  </div>

  <DocumentPreviewModal
    :show="showPreview"
    :docId="previewId"
    @close="showPreview = false"
  />
</template>

