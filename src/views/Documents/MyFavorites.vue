<script setup>
import { ref, onMounted } from "vue";
import api from "@/api";
import DocumentPreviewModal from "@/views/Documents/DocumentPreviewModal.vue";
import { useToast } from "vue-toastification";

const toast = useToast();

const documents = ref([]);
const loading = ref(true);
const error = ref("");

const showPreview = ref(false);
const previewId = ref(null);

const category = ref("")

const categories = [
  "General",
  "Administrative",
  "Academics",
  "Research",
  "Policies",
  "Official Issuances",
  "News & Events"
]

async function fetchFavorites() {
  loading.value = true;
  error.value = "";

  try {
    const res = await api.get("/documents/my-favorites");
    documents.value = res.data;
  } catch (err) {
    console.error(err);
    error.value = "Failed to load favorites.";
  } finally {
    loading.value = false;
  }
}

function openPreview(id) {
  previewId.value = id;
  showPreview.value = true;
}

async function toggleFavorite(doc) {
  try {
    const res = await api.post(`/documents/${doc.id}/favorite`);

    // ⭐ If removed → instantly remove from UI
    if (res.data.status === "removed") {
      documents.value = documents.value.filter(d => d.id !== doc.id);
      toast.success("Removed from favorites");
    }

  } catch (err) {
    console.error(err);
    toast.error("Action failed");
  }
}

onMounted(fetchFavorites);
</script>


<template>
  <div class="p-8">
    <h1 class="text-2xl font-bold mb-6">My Favorites</h1>

    <div v-if="loading">Loading...</div>
    <div v-if="error" class="text-red-600">{{ error }}</div>

    <table v-if="documents.length" class="w-full bg-white shadow rounded-lg">
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
          v-for="doc in documents"
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
              class="bg-blue-600 text-white px-4 py-2 rounded"
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

    <div
      v-if="!loading && documents.length === 0"
      class="text-gray-600 text-center mt-6"
    >
      No favorite documents yet.
    </div>
  </div>

  <DocumentPreviewModal
    :show="showPreview"
    :docId="previewId"
    @close="showPreview = false"
  />
</template>
