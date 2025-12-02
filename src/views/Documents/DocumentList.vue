<script setup>
import { ref, onMounted } from "vue";
import api from "@/api";

const documents = ref([]);
const loading = ref(true);
const error = ref("");
const search = ref("");

const role = ref(localStorage.getItem("role")); // ROLE STORED HERE

// Fetch all documents
async function fetchDocuments() {
  loading.value = true;

  try {
    const res = await api.get("/documents/list");
    documents.value = res.data;
  } catch (err) {
    console.error("Error loading documents:", err);
    error.value = "Unable to load documents.";
  } finally {
    loading.value = false;
  }
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

// Load on page load
onMounted(() => {
  fetchDocuments();
});
</script>

<template>
  <div class="p-8">
    <div class="flex justify-between items-center mb-4">
      <h1 class="text-xl font-semibold text-dns_dark">Documents</h1>
      <router-link v-if="role==='Admin'"
        to="/documents/upload"
        class="px-4 py-2 bg-dns_dark text-white rounded"
      >
        Upload
      </router-link>
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
          <th class="p-3 text-left">Description</th>
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
          <td class="p-3">{{ doc.description }}</td>
          <td class="p-3">{{ doc.uploaded_by }}</td>
          <td class="p-3">{{ doc.uploaded_at }}</td>

          <td class="p-3 text-center">
            <button
              @click="downloadFile(doc.filename)"
              class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
            >
              Download
            </button>
          </td>

          <td class="p-3 text-center">
            <!-- FIXED ROLE CHECK -->
            <button
              v-if="role === 'Admin'"
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
</template>
