<script setup>
import { ref, onMounted } from "vue";
import api from "@/api";
import { useToast } from "vue-toastification";

const toast = useToast();

const requests = ref([]);
const loading = ref(true);
const error = ref("");

/* 📥 Load requests */
async function loadRequests() {
  loading.value = true;
  error.value = "";

  try {
    const res = await api.get("/documents/my-download-requests");
    requests.value = res.data;
  } catch (err) {
    console.error(err);
    error.value = "Failed to load download requests.";
    toast.error(error.value);
  } finally {
    loading.value = false;
  }
}

/* ⬇ Download approved file */
function downloadDocument(docId) {
  const token = localStorage.getItem("token");

  if (!token) {
    toast.error("Not authenticated");
    return;
  }

  const downloadUrl = `http://127.0.0.1:8000/documents/download/${docId}?token=${token}`;

  // ✅ use same tab navigation (no async extension warning)
  window.location.href = downloadUrl;

  // ⏳ refresh list after backend marks as used
  setTimeout(() => {
    loadRequests();
  }, 800);
}

/* 🎨 Status color helper */
function statusClass(status) {
  return {
    PENDING: "text-yellow-600",
    APPROVED: "text-green-600",
    REJECTED: "text-red-600"
  }[status] || "text-gray-500";
}

onMounted(loadRequests);
</script>

<template>
  <div class="p-8">
    <h1 class="text-2xl font-semibold mb-6">
      My Download Requests
    </h1>

    <!-- 🔄 Loading -->
    <div v-if="loading" class="text-gray-600">
      Loading requests...
    </div>

    <!-- ❌ Error -->
    <div v-else-if="error" class="text-red-600">
      {{ error }}
    </div>

    <!-- 📭 Empty -->
    <div
      v-else-if="requests.length === 0"
      class="text-gray-500 text-center mt-10"
    >
      No download requests found.
    </div>

    <!-- 📄 Table -->
    <table
      v-else
      class="w-full bg-white shadow rounded-lg overflow-hidden"
    >
      <thead class="bg-green-700 text-white">
        <tr>
          <th class="p-3 text-left">Document</th>
          <th class="p-3 text-left">Reason</th>
          <th class="p-3 text-left">Requested At</th>
          <th class="p-3 text-left">Status</th>
          <th class="p-3 text-center">Action</th>
        </tr>
      </thead>

      <tbody>
        <tr
          v-for="r in requests"
          :key="r.id"
          class="border-b hover:bg-gray-50"
        >
          <td class="p-3 font-medium">
            {{ r.document_name }}
          </td>

          <td class="p-3">
            {{ r.reason || "—" }}
          </td>

          <td class="p-3">
            {{ r.requested_at }}
          </td>

          <td class="p-3 font-semibold">
            <span :class="statusClass(r.status)">
              {{ r.status }}
            </span>
          </td>

          <td class="p-3 text-center">
            <button
              v-if="r.status === 'APPROVED'"
              @click="downloadDocument(r.document_id)"
              class="px-4 py-2 bg-green-700 text-white rounded hover:bg-green-800"
            >
              Download
            </button>

            <span v-else class="text-gray-400">
              —
            </span>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
