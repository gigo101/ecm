<script setup>
import { ref, onMounted } from "vue";
import api from "@/api";
import DocumentPreviewModal from "@/views/Documents/DocumentPreviewModal.vue";

const documents = ref([]);
const loading = ref(true);
const error = ref("");
const search = ref("");
const showPreview = ref(false);
const previewId = ref(null);

const role = ref(localStorage.getItem("role")); // ROLE STORED HERE
const activeTab = ref("all"); // all | mine

// Fetch all documents
async function fetchDocuments() {
  loading.value = true;
  error.value = "";

  try {
    const url =
      activeTab.value === "mine"
        ? "/documents/my-uploads"
        : "/documents/list";

    const res = await api.get(url);
    documents.value = res.data;
  } catch (err) {
    error.value = "Unable to load documents.";
  } finally {
    loading.value = false;
  }
}

function switchTab(tab) {
  activeTab.value = tab;
  fetchDocuments();
}

// Search filter
function filteredDocuments() {
  if (!search.value) return documents.value;
  return documents.value.filter(d =>
    d.filename.toLowerCase().includes(search.value.toLowerCase()) ||
    d.description?.toLowerCase().includes(search.value.toLowerCase())
  );
}

// Download
function downloadFile(filename) {
  window.open(`http://127.0.0.1:8000/uploads/${filename}`, "_blank");
}

// Delete
async function deleteDocument(id) {
  if (!confirm("Are you sure you want to delete this document?")) return;

  try {
    await api.delete(`/documents/${id}`);
    alert("Document deleted successfully!");

    // Reload
    fetchDocuments();
  } catch (err) {
    console.error("Delete error:", err);
    alert("Failed to delete document.");
  }
}




function openPreview(id) {
  previewId.value = id;
  showPreview.value = true;
}

// Load on page load
onMounted(() => {
  fetchDocuments();
});
</script>

<template>
  <div class="p-8">
    <div class="flex justify-between items-center mb-4">
      <h1 class="text-xl font-semibold text-dns_dark">Documents</h1>
      <router-link v-if="role==='Admin' || role==='Uploader'"
        to="/documents/upload"
        class="px-4 py-2 bg-dns_dark text-white rounded"
      >
        Upload
      </router-link>
    </div>
<div  v-if="role === 'Admin' || role === 'Uploader'" class="flex gap-4 mb-4">
  <button
    @click="switchTab('all')"
    :class="activeTab === 'all'
      ? 'bg-green-700 text-white'
      : 'bg-gray-200 text-gray-700'"
    class="px-4 py-2 rounded"
  >
    All Documents
  </button>

  <!-- Admin & Uploader only -->
  <button
    v-if="role === 'Admin' || role === 'Uploader'"
    @click="switchTab('mine')"
    :class="activeTab === 'mine'
      ? 'bg-green-700 text-white'
      : 'bg-gray-200 text-gray-700'"
    class="px-4 py-2 rounded"
  >
    My Uploads
  </button>
</div>

    <!-- Search bar -->
    <input
      v-model="search"
      type="text"
      placeholder="Search documents..."
      class="w-full p-3 mb-4 border rounded-lg focus:ring-2 focus:ring-green-500"
    />

    <div v-if="loading" class="text-gray-600">Loading...</div>
    <div v-if="error" class="text-red-600">{{ error }}</div>

    <table v-if="!loading" class="w-full bg-white shadow-lg rounded-lg overflow-hidden">
      <thead class="bg-green-700 text-white">
        <tr>
          <th class="p-3 text-left">Filename</th>
          <!-- <th class="p-3 text-left">Description</th> -->
          <th class="p-3 text-left">Category</th>
          <th class="p-3 text-left">Type</th>
          <th class="p-3 text-left">Uploaded By</th>
          <th class="p-3 text-left">Date</th>
          <th class="p-3 text-center" colspan="2">Action</th>
        </tr>
      </thead>

      <tbody>
        <tr
          v-for="doc in filteredDocuments()"
          :key="doc.id"
          class="border-b hover:bg-gray-100"
        >
          <td class="p-3">{{ doc.filename }}</td>
          <!-- <td class="p-3">{{ doc.description }}</td> -->
          <td class="p-3">{{ doc.category }}</td>
          <td class="p-3 font-semibold">
          <span v-if="doc.document_type === 'Confidential'" class="text-red-600">
            {{ doc.document_type }}
          </span>
          <span v-else class="text-green-700">
            {{ doc.document_type }}
          </span>
</td>
          <td class="p-3">{{ doc.uploaded_by }}</td>
          <td class="p-3">{{ doc.uploaded_at }}</td>

          <td class="p-3 text-center">
            <button v-if="role==='Admin' || role==='Uploader' || role==='Faculty' || role==='Staff' || role==='Management'"
              @click="downloadFile(doc.filename)"
              class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
            >
              Download
            </button>
            <button v-if="role==='Viewer'"
              @click="openPreview(doc.id)"
              class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
            >
              View
            </button>
          </td>

          <td class="p-3 text-center">
            <!-- FIXED ROLE CHECK -->
            <button
              v-if="role === 'Admin' || role === 'Uploader'"
              @click="deleteDocument(doc.id)"
              class="px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700"
            >
              Delete
            </button>
          </td>
        </tr>
      </tbody>
    </table>

    <div v-if="!loading && filteredDocuments().length === 0"
         class="text-gray-600 text-center mt-4">
      No documents found.
    </div>
  </div>

  <DocumentPreviewModal
  :show="showPreview"
  :docId="previewId"
  @close="showPreview = false"
/>

</template>
