<script setup>
import { ref, onMounted } from "vue"
import api from "@/api"
import DocumentPreviewModal from "@/views/Documents/DocumentPreviewModal.vue"
import { useToast } from "vue-toastification"

const documents = ref([])
const loading = ref(true)
const error = ref("")
const showPreview = ref(false)
const previewId = ref(null)
const toast = useToast()

const role = ref(localStorage.getItem("role"))

async function fetchSharedDocuments() {
  loading.value = true
  error.value = ""

  try {
    const res = await api.get("/documents/shared-with-me")
    documents.value = res.data
  } catch {
    error.value = "Failed to load shared documents."
  } finally {
    loading.value = false
  }
}

function openPreview(id) {
  previewId.value = id
  showPreview.value = true
}

function downloadFile(doc) {
  const token = localStorage.getItem("token")

  window.open(
    `http://127.0.0.1:8000/documents/download/${doc.id}?token=${token}`,
    "_blank"
  )
}

async function toggleFavorite(doc) {
  try {
    const res = await api.post(`/documents/${doc.id}/favorite`)
    doc.is_favorite = res.data.status === "added"
  } catch {
    toast.error("Failed to update favorite")
  }
}

onMounted(fetchSharedDocuments)
</script>

<template>
  <div class="p-8">

    <!-- HEADER -->
    <h1 class="text-xl font-semibold text-dns_dark mb-4">
      Shared With Me
    </h1>

    <div v-if="loading">Loading...</div>
    <div v-if="error" class="text-red-600">{{ error }}</div>

    <!-- TABLE -->
    <table
      v-if="!loading && documents.length"
      class="w-full bg-white shadow-lg rounded-lg overflow-hidden"
    >
      <thead class="bg-green-700 text-white">
        <tr>
          <th class="p-3 text-left">Filename</th>
          <th class="p-3 text-left">Category</th>
          <th class="p-3 text-left">Type</th>
          <th class="p-3 text-left">Uploaded By</th>
          <th class="p-3 text-left">Date</th>
          <th class="p-3 text-center">Actions</th>
          <th class="p-3"></th>
        </tr>
      </thead>

      <tbody>
        <tr
          v-for="doc in documents"
          :key="doc.id"
          class="border-b hover:bg-gray-100"
        >
          <td class="p-3">{{ doc.filename }}</td>
          <td class="p-3">{{ doc.category }}</td>

          <td class="p-3 font-semibold">
            <span
              v-if="doc.document_type === 'Confidential'"
              class="text-red-600"
            >
              {{ doc.document_type }}
            </span>
            <span v-else class="text-green-700">
              {{ doc.document_type }}
            </span>
          </td>

          <td class="p-3">{{ doc.uploaded_by }}</td>
          <td class="p-3">{{ doc.uploaded_at }}</td>

          <!-- ACTIONS -->
          <td class="p-3">
            <div class="flex justify-center gap-2">

              <button
                @click="openPreview(doc.id)"
                class="bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700"
              >
                Preview
              </button>

              <button
                v-if="role !== 'Viewer'"
                @click="downloadFile(doc)"
                class="bg-green-600 text-white px-3 py-1 rounded hover:bg-green-700"
              >
                Download
              </button>

            </div>
          </td>

          <!-- FAVORITE -->
          <td class="p-3 text-center">
            <button
              @click="toggleFavorite(doc)"
              class="px-3 py-2 rounded"
              :class="doc.is_favorite
                ? 'bg-yellow-500 text-white'
                : 'bg-gray-300'"
            >
              ★
            </button>
          </td>

        </tr>
      </tbody>
    </table>

    <!-- EMPTY STATE -->
    <div
      v-if="!loading && documents.length === 0"
      class="text-center text-gray-500 mt-6"
    >
      No shared documents.
    </div>

  </div>

  <!-- PREVIEW MODAL -->
  <DocumentPreviewModal
    :show="showPreview"
    :docId="previewId"
    source="LIST"
    @close="showPreview = false"
  />
</template>