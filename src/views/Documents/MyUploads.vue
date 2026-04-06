<script setup>
import { ref, onMounted, computed } from "vue"
import api from "@/api"
import DocumentPreviewModal from "@/views/Documents/DocumentPreviewModal.vue"
import { useToast } from "vue-toastification"
import 'primeicons/primeicons.css'

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

// SHARE STATES
const showShareModal = ref(false)
const selectedDoc = ref(null)
const users = ref([])
const selectedUsers = ref([])
const existingShares = ref([])
const userSearch = ref("")

const openMenuId = ref(null)

function toggleMenu(id) {
  openMenuId.value = openMenuId.value === id ? null : id
}

// COMPUTED: Filter available users
const availableUsers = computed(() => {
  return users.value
    .filter(u =>
      !existingShares.value.some(s => s.shared_to === u.email)
    )
    .filter(u => {
      const term = userSearch.value.toLowerCase()
      return (
        u.first_name.toLowerCase().includes(term) ||
        u.last_name.toLowerCase().includes(term) ||
        u.email.toLowerCase().includes(term)
      )
    })
})

// ============================
// FETCH MY UPLOADS
// ============================
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

  } catch {
    error.value = "Unable to load your uploads."
  } finally {
    loading.value = false
  }
}

// ============================
// PAGINATION
// ============================
function changePage(newPage) {
  if (newPage < 1 || newPage > totalPages.value) return
  page.value = newPage
  fetchMyUploads()
}

// ============================
// PREVIEW
// ============================
function openPreview(id) {
  previewId.value = id
  showPreview.value = true
}

// ============================
// DOWNLOAD
// ============================
function downloadFile(filename) {
  const baseUrl = import.meta.env.VITE_API_URL
  window.open(`${baseUrl}/uploads/${filename}`, "_blank")
}

// ============================
// DELETE
// ============================
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

// ============================
// SHARE LOGIC
// ============================
async function loadUsers() {
  try {
    const res = await api.get("/users")
    users.value = res.data
  } catch {
    toast.error("Failed to load users")
  }
}

async function openShareModal(doc) {
  selectedDoc.value = doc
  selectedUsers.value = []
  userSearch.value = ""
  showShareModal.value = true

  await loadUsers()

  const res = await api.get(`/documents/${doc.id}/shares`)
  existingShares.value = res.data
}

async function revokeAccess(email) {
  try {
    await api.delete(
      `/documents/${selectedDoc.value.id}/share/${email}`
    )

    existingShares.value =
      existingShares.value.filter(s => s.shared_to !== email)

    toast.success("Access revoked")
  } catch {
    toast.error("Failed to revoke access")
  }
}

async function shareDocument() {
  try {

    if (selectedUsers.value.length === 0) {
      toast.warning("Select at least one user")
      return
    }

    await api.post(`/documents/${selectedDoc.value.id}/share`, {
      users: selectedUsers.value
    })

    toast.success("Document shared successfully")

    setTimeout(() => {
      showShareModal.value = false
    }, 200)

  } catch {
    toast.error("Failed to share document")
  }
}

onMounted(fetchMyUploads)
</script>

<template>
  <div class="p-8">

    <!-- HEADER -->
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

    <!-- TABLE -->
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
          v-for="(doc, index) in documents"
          :key="doc.id"
          class="border-b hover:bg-gray-100"
        >
          <td class="p-3">
            <div class="font-medium">
              {{ doc.filename }}
            </div>

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
<td class="p-3">
  <div class="flex justify-center items-center gap-1">

    <!-- PREVIEW -->
    <button
      @click="openPreview(doc.id)"
      class="p-2 w-9 h-9 flex items-center justify-center rounded hover:bg-gray-200 transition"
      title="Preview"
    >
      <i class="pi pi-eye"></i>
    </button>

    <!-- DOWNLOAD -->
    <button
      @click="downloadFile(doc.filename)"
      class="p-2 w-9 h-9 flex items-center justify-center rounded hover:bg-gray-200 transition"
      title="Download"
    >
      <i class="pi pi-download"></i>
    </button>

    <!-- MORE MENU -->
    <div class="relative">

      <button
        @click="toggleMenu(doc.id)"
        class="p-2 w-9 h-9 flex items-center justify-center rounded hover:bg-gray-200 transition"
        title="More"
      >
        <i class="pi pi-ellipsis-v"></i>
      </button>

      <!-- DROPDOWN -->
    <div
  v-if="openMenuId === doc.id"
  :class="[
    'absolute right-0 w-36 bg-white border rounded shadow-lg z-50',
    index >= documents.length - 2
      ? 'bottom-full mb-2'
      : 'mt-2'
  ]"
>

        <button
          v-if="role==='Admin' || role==='Uploader'"
          @click="openShareModal(doc); openMenuId = null"
          class="flex items-center gap-2 w-full px-3 py-2 hover:bg-gray-100"
        >
          <i class="pi pi-share-alt"></i>
          Share
        </button>

        <button
          @click="deleteDocument(doc.id); openMenuId = null"
          class="flex items-center gap-2 w-full px-3 py-2 text-red-600 hover:bg-gray-100"
        >
          <i class="pi pi-trash"></i>
          Delete
        </button>

      </div>

    </div>

  </div>
</td>
        </tr>
      </tbody>
    </table>

    <div v-if="!loading && documents.length === 0" class="text-gray-600">
      You haven’t uploaded any documents yet.
    </div>

    <!-- PAGINATION -->
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

  <!-- SHARE MODAL -->
  <div
    v-if="showShareModal"
    class="fixed inset-0 bg-black/40 flex items-center justify-center z-50"
  >
    <div class="bg-white p-6 rounded-lg w-96 shadow-lg">

      <h2 class="text-lg font-bold mb-3">
        Share {{ selectedDoc?.filename }}
      </h2>

      <div v-if="existingShares.length" class="mb-3">
        <p class="font-semibold text-sm mb-1">Currently shared with:</p>

        <div
          v-for="s in existingShares"
          :key="s.shared_to"
          class="flex justify-between items-center bg-gray-100 px-2 py-1 rounded mb-1"
        >
          <span class="text-sm">{{ s.shared_to }}</span>

          <button
            @click="revokeAccess(s.shared_to)"
            class="text-red-600 text-xs hover:underline"
          >
            Remove
          </button>
        </div>
      </div>

      <input
        v-model="userSearch"
        type="text"
        placeholder="Search user..."
        class="w-full border p-2 mb-2 rounded"
      />

      <select
        v-model="selectedUsers"
        multiple
        class="w-full border p-2 mb-4 h-40"
      >
        <option
          v-for="u in availableUsers"
          :key="u.email"
          :value="u.email"
        >
          {{ u.first_name }} {{ u.last_name }} — {{ u.email }}
        </option>

        <option v-if="availableUsers.length === 0" disabled>
          No users found
        </option>
      </select>

      <p class="text-xs text-gray-500 mb-3">
        {{ selectedUsers.length }} user(s) selected
      </p>

      <div class="flex justify-end gap-2">
        <button
          @click="showShareModal=false"
          class="px-3 py-1 bg-gray-300 rounded"
        >
          Cancel
        </button>

        <button
          @click="shareDocument"
          class="px-3 py-1 bg-purple-600 text-white rounded"
        >
          Share
        </button>
      </div>

    </div>
  </div>

  <!-- PREVIEW MODAL -->
  <DocumentPreviewModal
    :show="showPreview"
    :docId="previewId"
    @close="showPreview = false"
  />
</template>