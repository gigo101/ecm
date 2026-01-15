<script setup>
import { ref, onMounted } from "vue";
import api from "@/api";
import { useToast } from "vue-toastification";

const toast = useToast();
const requests = ref([]);
const loading = ref(true);

async function loadRequests() {
  loading.value = true;
  const res = await api.get("/documents/my-download-requests");
  requests.value = res.data;
  loading.value = false;
}

function downloadDocument(docId) {
  const token = localStorage.getItem("token");

  if (!token) {
    toast.error("Not authenticated");
    return;
  }

  window.open(
    `http://127.0.0.1:8000/documents/download/${docId}?token=${token}`,
    "_blank"
  );

  // ⏳ Small delay to allow backend to mark as downloaded
  setTimeout(() => {
    loadRequests(); // refresh list
  }, 800);

}

onMounted(loadRequests);
</script>

<template>
  <div class="p-8">
    <h1 class="text-2xl font-semibold mb-6">
      My Download Requests
    </h1>

    <div v-if="loading">Loading...</div>

    <table v-else class="w-full bg-white shadow rounded-lg">
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
        <tr v-for="r in requests" :key="r.id" class="border-b">
          <td class="p-3">{{ r.document_name }}</td>
          <td class="p-3">{{ r.reason || "—" }}</td>
          <td class="p-3">{{ r.requested_at }}</td>

          <td class="p-3 font-semibold">
            <span
              :class="{
                'text-yellow-600': r.status === 'PENDING',
                'text-green-600': r.status === 'APPROVED',
                'text-red-600': r.status === 'REJECTED'
              }"
            >
              {{ r.status }}
            </span>
          </td>

          <td class="p-3 text-center">
            <button
              v-if="r.status === 'APPROVED'"
              @click="downloadDocument(r.document_id)"
              class="px-4 py-2 bg-green-700 text-white rounded"
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
