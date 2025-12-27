<script setup>
import { ref, onMounted } from "vue";
import api from "@/api";
import { useToast } from "vue-toastification";

const toast = useToast();
const requests = ref([]);
const loading = ref(true);

async function loadRequests() {
  loading.value = true;
  const res = await api.get("/admin/download-requests");
  requests.value = res.data;
  loading.value = false;
}

async function updateStatus(id, status) {
  try {
    await api.put(`/admin/download-requests/${id}`, null, {
      params: { status }
    });

    toast.success(`Request ${status.toLowerCase()} successfully`);
    loadRequests();
  } catch {
    toast.error("Failed to update request");
  }
}

onMounted(loadRequests);
</script>

<template>
  <div class="p-8">
    <h1 class="text-2xl font-semibold mb-6">
      Download Requests
    </h1>

    <div v-if="loading">Loading requests...</div>

    <table v-else class="w-full bg-white shadow rounded-lg">
      <thead class="bg-green-700 text-white">
        <tr>
          <th class="p-3 text-left">Document</th>
          <th class="p-3 text-left">Requested By</th>
          <th class="p-3 text-left">Reason</th>
          <th class="p-3 text-left">Date</th>
          <th class="p-3 text-left">Status</th>
          <th class="p-3 text-center">Action</th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="r in requests" :key="r.id" class="border-b">
          <td class="p-3">{{ r.document_name }}</td>
          <td class="p-3">{{ r.requester_email }}</td>
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
            <div v-if="r.status === 'PENDING'" class="flex justify-center gap-2">
              <button
                @click="updateStatus(r.id, 'APPROVED')"
                class="px-3 py-1 bg-green-700 text-white rounded"
              >
                Approve
              </button>

              <button
                @click="updateStatus(r.id, 'REJECTED')"
                class="px-3 py-1 bg-red-600 text-white rounded"
              >
                Reject
              </button>
            </div>
            <span v-else>—</span>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
