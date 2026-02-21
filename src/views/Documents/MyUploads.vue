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
const page = ref(1)
const limit = ref(10)
const totalPages = ref(1)

async function fetchMyUploads() {
  loading.value = true
  error.value = ""

  try {
    const res = await api.get("/documents/my-uploads", {
      params: {
        page: page.value,
        limit: limit.value
      }
    })

    documents.value = res.data.data
    totalPages.value = res.data.pages

  } catch (err) {
    error.value = "Unable to load your uploads."
  } finally {
    loading.value = false
  }
}

function changePage(newPage) {
  if (newPage < 1 || newPage > totalPages.value) return
  page.value = newPage
  fetchMyUploads()
}

function openPreview(id) {
  previewId.value = id
  showPreview.value = true
}

function downloadFile(filename) {
  window.open(`http://127.0.0.1:8000/uploads/${filename}`, "_blank")
}

async function deleteDocument(id) {
  if (!confirm("Are you sure you want to delete this document?")) return

  try {
    await api.delete(`/documents/${id}`)

    if (documents.value.length === 1 && page.value > 1) {
      page.value--
    }

    fetchMyUploads()
    toast.success("Document deleted successfully.")
  } catch {
    toast.error("Failed to delete document.")
  }
}

onMounted(fetchMyUploads)
</script>

<template>
  <div class="p-8">

    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold text-dns_dark">My Uploads</h1>

      <router-link
        to="/documents/upload"
        class="px-4 py-2 bg-dns_dark text-white rounded"
      >
        Upload
      </router-link>
    </div>

    <div v-if="loading">Loading...</div>
    <div v-if="error" class="text-red-600">{{ error }}</div>

    <table
      v-if="documents.length"
      class="w-full bg-white shadow-lg rounded-lg overflow-hidden"
    >
      <thead class="bg-green-700 text-white">
        <tr>
          <th class="p-3 text-left">Filename</th>
          <th class="p-3 text-left">Category</th>
          <th class="p-3 text-left">Type</th>
          <th class="p-3 text-left">Year</th>
          <th class="p-3 text-left">Uploaded By</th>
          <th class="p-3 text-left">Date</th>
          <th class="p-3 text-center">Action</th>
        </tr>
      </thead>

      <tbody>
        <tr
          v-for="doc in documents"
          :key="doc.id"
          class="border-b hover:bg-gray-100"
        >
          <td class="p-3">
              <div class="font-medium">
                {{ doc.filename }}
              </div>

              <!-- 👥 SHARED COUNT -->
              <div
                v-if="doc.shared_count > 0 && (role === 'Admin' || role === 'Uploader')"
                class="text-xs text-purple-600"
              >
                Shared with {{ doc.shared_count }} user(s)
              </div>
          </td>
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

          <td class="p-3">{{ doc.year_approved }}</td>
          <td class="p-3">{{ doc.uploaded_by }}</td>
          <td class="p-3">{{ doc.uploaded_at }}</td>

          <td class="p-3 text-center">
            <div class="flex justify-center gap-2">

              <button
                @click="openPreview(doc.id)"
                class="bg-blue-600 text-white px-4 py-2 rounded"
              >
                Preview
              </button>

              <button
                @click="downloadFile(doc.filename)"
                class="bg-green-600 text-white px-4 py-2 rounded"
              >
                Download
              </button>

              <button
                @click="deleteDocument(doc.id)"
                class="bg-red-600 text-white px-4 py-2 rounded"
              >
                Delete
              </button>

            </div>
          </td>
        </tr>
      </tbody>
    </table>

    <div v-if="!loading && documents.length === 0" class="text-gray-600">
      You haven’t uploaded any documents yet.
    </div>

    <!-- ⭐ PAGINATION -->
    <div class="flex justify-center items-center gap-4 mt-6">
      <button
        @click="changePage(page - 1)"
        :disabled="page === 1"
        class="px-4 py-2 bg-gray-300 rounded disabled:opacity-50"
      >
        Prev
      </button>

      <span class="font-semibold">
        Page {{ page }} of {{ totalPages }}
      </span>

      <button
        @click="changePage(page + 1)"
        :disabled="page === totalPages"
        class="px-4 py-2 bg-gray-300 rounded disabled:opacity-50"
      >
        Next
      </button>
    </div>

  </div>

  <DocumentPreviewModal
    :show="showPreview"
    :docId="previewId"
    @close="showPreview = false"
  />
</template>
