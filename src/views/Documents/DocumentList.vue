<script setup>
import { ref, onMounted } from "vue";
import api from "@/api";
import DocumentPreviewModal from "@/views/Documents/DocumentPreviewModal.vue";
import { useToast } from "vue-toastification";
import { computed } from "vue"

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

const showShareModal = ref(false);
const selectedDoc = ref(null);
const users = ref([]);
const selectedUsers = ref([]);
const existingShares = ref([]);
const userSearch = ref("");

async function loadUsers() {
  try {
    const res = await api.get("/users")
    users.value = res.data
  } catch {
    toast.error("Failed to load users")
  }
}

// function openShareModal(doc) {
//   selectedDoc.value = doc
//   selectedUsers.value = []
//   showShareModal.value = true
//   loadUsers()
// }

async function openShareModal(doc) {
  selectedDoc.value = doc
  selectedUsers.value = []
  userSearch.value = ""   // ⭐ reset search
  showShareModal.value = true

  await loadUsers()

  const res = await api.get(`/documents/${doc.id}/shares`)
  existingShares.value = res.data
}

async function revokeAccess(email) {
  await api.delete(
    `/documents/${selectedDoc.value.id}/share/${email}`
  )

  existingShares.value =
    existingShares.value.filter(s => s.shared_to !== email)

  toast.success("Access revoked")
}


// async function shareDocument() {
//     await api.post(`/documents/${selectedDoc.value.id}/share`, {
//       users: selectedUsers.value
//     })

//     const res = await api.get(`/documents/${selectedDoc.value.id}/shares`)
//     existingShares.value = res.data
//     selectedUsers.value = []
// }

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

    // ⏳ allow toast to render first
    setTimeout(() => {
      showShareModal.value = false
    }, 200)

  } catch (err) {
    toast.error("Failed to share document")
  }
}

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
        <!-- RESULT COUNT -->
    <p class="text-sm text-gray-600 mb-2">
      Showing {{ filteredDocuments().length }} result(s)
    </p>

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

              <button
                  v-if="role==='Admin' || role==='Uploader'"
                  @click="openShareModal(doc)"
                  class="bg-purple-600 text-white px-3 py-1 rounded hover:bg-purple-700"
                >
                  Share
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

   <div
  v-if="showShareModal"
  class="fixed inset-0 bg-black/40 flex items-center justify-center z-50"
>
  <div class="bg-white p-6 rounded-lg w-96 shadow-lg">

    <h2 class="text-lg font-bold mb-3">
      Share {{ selectedDoc?.filename }}
    </h2>

    <!-- USER MULTI SELECT -->
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
