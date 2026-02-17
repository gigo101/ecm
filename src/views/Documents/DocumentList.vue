<script setup>
import { ref, onMounted } from "vue";
import api from "@/api";
import DocumentPreviewModal from "@/views/Documents/DocumentPreviewModal.vue";
import { useToast } from "vue-toastification";

const documents = ref([]);
const loading = ref(true);
const error = ref("");
const search = ref("");
const showPreview = ref(false);
const previewId = ref(null);
const toast = useToast();

const role = ref(localStorage.getItem("role"));

const page = ref(1);
const limit = ref(10);
const totalPages = ref(1);

async function fetchDocuments() {
  loading.value = true;
  error.value = "";

  try {
    const res = await api.get("/documents/list", {
      params: {
        page: page.value,
        limit: limit.value
      }
    });

    documents.value = res.data.data;
    totalPages.value = res.data.pages;

  } catch {
    error.value = "Unable to load documents.";
  } finally {
    loading.value = false;
  }
}

function changePage(newPage) {
  if (newPage < 1 || newPage > totalPages.value) return;
  page.value = newPage;
  fetchDocuments();
}

function filteredDocuments() {
  if (!search.value) return documents.value;

  return documents.value.filter(d =>
    d.filename.toLowerCase().includes(search.value.toLowerCase()) ||
    d.description?.toLowerCase().includes(search.value.toLowerCase())
  );
}

function downloadFile(filename) {
  window.open(`http://127.0.0.1:8000/uploads/${filename}`, "_blank");
}

async function deleteDocument(id) {
  if (!confirm("Are you sure you want to delete this document?")) return;

  try {
    await api.delete(`/documents/${id}`);

    if (documents.value.length === 1 && page.value > 1) {
      page.value--;
    }

    fetchDocuments();
    toast.success("Document deleted successfully.");
  } catch {
    toast.error("Failed to delete document.");
  }
}

async function toggleFavorite(doc) {
  try {
    const res = await api.post(`/documents/${doc.id}/favorite`);
    doc.is_favorite = res.data.status === "added";
  } catch {
    toast.error("Failed to update favorite");
  }
}

function openPreview(id) {
  previewId.value = id;
  showPreview.value = true;
}

onMounted(fetchDocuments);
</script>

<template>
  <div class="p-8">

    <!-- HEADER -->
    <div class="flex justify-between items-center mb-4">
      <h1 class="text-xl font-semibold text-dns_dark">Documents</h1>

      <router-link
        v-if="role==='Admin' || role==='Uploader'"
        to="/documents/upload"
        class="px-4 py-2 bg-dns_dark text-white rounded"
      >
        Upload
      </router-link>
    </div>

    <!-- SEARCH -->
    <input
      v-model="search"
      type="text"
      placeholder="Search documents..."
      class="w-full p-3 mb-4 border rounded-lg focus:ring-2 focus:ring-green-500"
    />

    <div v-if="loading">Loading...</div>
    <div v-if="error" class="text-red-600">{{ error }}</div>

    <!-- TABLE -->
    <table v-if="!loading && filteredDocuments().length"
           class="w-full bg-white shadow-lg rounded-lg overflow-hidden">

      <thead class="bg-green-700 text-white">
        <tr>
          <th class="p-3 text-left">Filename</th>
          <th class="p-3 text-left">Category</th>
          <th class="p-3 text-left">Type</th>
          <th class="p-3 text-left">Year</th>
          <th class="p-3 text-left">Uploaded By</th>
          <th class="p-3 text-left">Date</th>
          <th class="p-3 text-center">Actions</th>
          <th class="p-3"></th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="doc in filteredDocuments()" :key="doc.id"
            class="border-b hover:bg-gray-100">

          <td class="p-3">{{ doc.filename }}</td>
          <td class="p-3">{{ doc.category }}</td>

          <td class="p-3 font-semibold">
            <span v-if="doc.document_type === 'Confidential'" class="text-red-600">
              {{ doc.document_type }}
            </span>
            <span v-else class="text-green-700">
              {{ doc.document_type }}
            </span>
          </td>

          <td class="p-3">{{ doc.year_approved }}</td>
          <td class="p-3">{{ doc.uploaded_by }}</td>
          <td class="p-3">{{ doc.uploaded_at }}</td>

          <!-- ACTIONS -->
          <td class="p-3">
            <div class="flex justify-center gap-2">

              <!-- PREVIEW -->
              <button
                @click="openPreview(doc.id)"
                class="bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700"
              >
                Preview
              </button>

              <!-- DOWNLOAD -->
              <button
                v-if="role !== 'Viewer'"
                @click="downloadFile(doc.filename)"
                class="bg-green-600 text-white px-3 py-1 rounded hover:bg-green-700"
              >
                Download
              </button>

              <!-- DELETE -->
              <button
                v-if="role === 'Admin' || role === 'Uploader'"
                @click="deleteDocument(doc.id)"
                class="bg-red-600 text-white px-3 py-1 rounded hover:bg-red-700"
              >
                Delete
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
    <div v-if="!loading && filteredDocuments().length === 0"
         class="text-center text-gray-500 mt-6">
      No documents found.
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

  <!-- PREVIEW MODAL -->
  <DocumentPreviewModal
    :show="showPreview"
    :docId="previewId"
    @close="showPreview = false"
  />
</template>
