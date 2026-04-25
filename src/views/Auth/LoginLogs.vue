<script setup>
import { ref, onMounted } from "vue";
import api from "@/api";

const logs = ref([]);
const loading = ref(false);
const error = ref("");

async function fetchLogs() {
  try {
    loading.value = true;
    const res = await api.get("/admin/login-logs");
    logs.value = res.data;
  } catch (err) {
    console.error(err);
    error.value = "Failed to load login logs";
  } finally {
    loading.value = false;
  }
}

onMounted(fetchLogs);
</script>

<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold mb-4">Login Activity Logs</h1>

    <div v-if="loading">Loading logs...</div>
    <div v-if="error" class="text-red-500">{{ error }}</div>

    <div v-if="!loading && logs.length === 0">
      No login activity found.
    </div>

    <div class="overflow-x-auto mt-4" v-if="logs.length">
      <table class="min-w-full bg-white shadow rounded-lg">
        <thead class="bg-green-700 text-white">
          <tr>
            <th class="p-3 text-left">Email</th>
            <th class="p-3 text-left">Status</th>
            <th class="p-3 text-left">IP Address</th>
            <th class="p-3 text-left">Device</th>
            <th class="p-3 text-left">Time</th>
          </tr>
        </thead>

        <tbody>
          <tr
            v-for="(log, index) in logs"
            :key="index"
            class="border-b hover:bg-gray-50"
          >
            <td class="p-3">{{ log.email }}</td>

            <td class="p-3">
              <span
                :class="log.status === 'SUCCESS'
                  ? 'text-green-600 font-semibold'
                  : 'text-red-600 font-semibold'"
              >
                {{ log.status }}
              </span>
            </td>

            <td class="p-3">{{ log.ip_address }}</td>

            <td class="p-3 truncate max-w-xs">
              {{ log.device }}
            </td>

            <td class="p-3">{{ log.time }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>