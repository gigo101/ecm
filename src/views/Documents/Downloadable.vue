<script setup>
import { ref, onMounted, watch } from "vue"
import api from "@/api"
import DownloadablePreviewModal from "./DownloadablePreviewModal.vue"

const forms = ref([])
const loading = ref(true)
const error = ref("")
const search = ref("")

const page = ref(1)
const limit = ref(10)
const totalPages = ref(1)

const role = ref(localStorage.getItem("role"))

const showPreview = ref(false)
const previewId = ref(null)
import { useToast } from "vue-toastification"

const toast = useToast()

function openPreview(id) {
  previewId.value = id
  showPreview.value = true
}

async function fetchForms() {
  loading.value = true
  error.value = ""

  try {
    const res = await api.get("/downloadables/list", {
      params: {
        page: page.value,
        limit: limit.value
      }
    })

    if (res.data.data) {
      forms.value = res.data.data
      totalPages.value = res.data.pages
    } else {
      forms.value = res.data
    }

  } catch (err) {
    console.error(err)
    error.value = "Unable to load downloadable forms."
  } finally {
    loading.value = false
  }
}

function changePage(newPage) {
  if (newPage < 1 || newPage > totalPages.value) return
  page.value = newPage
}

watch(page, fetchForms)

function filteredForms() {
  if (!search.value) return forms.value

  return forms.value.filter(f =>
    f.filename.toLowerCase().includes(search.value.toLowerCase())
  )
}

function downloadFile(id) {
  const token = localStorage.getItem("token")
  const baseUrl = import.meta.env.VITE_API_URL;
  window.open(
    `${baseUrl}/downloadables/download/${id}?token=${token}`,
    "_blank"
  )
}


async function deleteFile(id) {
  if (!confirm("Delete this file?")) return

  try {
    await api.delete(`/downloadables/${id}`)

    toast.success("File deleted successfully 🗑️")

    // if last item on page → go back one page
    if (forms.value.length === 1 && page.value > 1) {
      page.value--
    }

    fetchForms()

  } catch (err) {
    console.error(err)
    toast.error("Failed to delete file")
  }
}


onMounted(fetchForms)

</script>


<template>
  <div class="p-8">

    <!-- HEADER -->
    <div class="flex justify-between items-center mb-4">
      <h1 class="text-xl font-semibold text-dns_dark">
        Downloadable Forms
      </h1>

      <router-link
        v-if="role === 'Admin' || role === 'Uploader'"
        to="/downloadables/upload"
        class="px-4 py-2 bg-dns_dark text-white rounded"
      >
        Upload
      </router-link>
    </div>

    <!-- SEARCH -->
    <div class="relative w-full max-w-md mb-4">
      <input
        v-model="search"
        type="text"
        placeholder="Search forms..."
        class="w-full p-3 pl-10 border rounded-lg focus:ring-2 focus:ring-green-500"
      />

      <svg
        class="absolute left-3 top-3.5 h-5 w-5 text-gray-400"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M21 21l-4.35-4.35M11 19a8 8 0 100-16 8 8 0 000 16z"
        />
      </svg>
    </div>

    <!-- STATES -->
    <div v-if="loading" class="text-gray-600">Loading...</div>
    <div v-if="error" class="text-red-600">{{ error }}</div>

    <!-- TABLE -->
    <table
      v-if="!loading && filteredForms().length"
      class="w-full bg-white shadow-lg rounded-lg overflow-hidden"
    >
      <thead class="bg-green-700 text-white">
        <tr>
          <th class="p-3 text-left">Filename</th>
          <th class="p-3 text-left">Uploaded By</th>
          <th class="p-3 text-left">Date</th>
          <th class="p-3 text-center">Preview</th>
          <th class="p-3 text-center">Download</th>
          <th
            v-if="role === 'Admin' || role === 'Uploader'"
            class="p-3 text-center"
            >
            Delete
         </th>

        </tr>
      </thead>

      <tbody>
        <tr
          v-for="form in filteredForms()"
          :key="form.id"
          class="border-b hover:bg-gray-100"
        >
          <td class="p-3">{{ form.filename }}</td>
          <td class="p-3">{{ form.uploaded_by }}</td>
          <td class="p-3">{{ form.uploaded_at }}</td>

          <!-- PREVIEW -->
          <td class="p-3 text-center">
            <button
              @click="openPreview(form.id)"
              class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
            >
              Preview
            </button>
          </td>

          <!-- DOWNLOAD -->
          <td class="p-3 text-center">
            <button
              @click="downloadFile(form.id)"
              class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
            >
              Download
            </button>
          </td>
          <td
            v-if="role === 'Admin' || role === 'Uploader'"
            class="p-3 text-center"
            >
            <button
                @click="deleteFile(form.id)"
                class="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
            >
                Delete
            </button>
          </td>

        </tr>
      </tbody>
    </table>

    <!-- EMPTY -->
    <div
      v-if="!loading && filteredForms().length === 0"
      class="text-gray-600 text-center mt-6"
    >
      No downloadable forms found.
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

<DownloadablePreviewModal
  :show="showPreview"
  :fileId="previewId"
  @close="showPreview = false"
/>


</template>
