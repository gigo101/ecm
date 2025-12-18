<script setup>
import { ref, onMounted } from "vue";
import api from "@/api";

const logs = ref([]);
const loading = ref(true);

onMounted(async () => {
  try {
    const res = await api.get("/admin/document-logs");
    logs.value = res.data;
  } catch (err) {
    alert("Failed to load document logs.");
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <div class="p-8">
    <h1 class="text-xl font-semibold mb-4">Document Access Logs</h1>

    <table class="w-full bg-white shadow rounded">
      <thead class="bg-green-700 text-white">
        <tr>
          <th class="p-3 text-left">Document</th>
          <th class="p-3 text-left">User</th>
          <th class="p-3 text-left">Action</th>
          <!-- <th class="p-3 text-left">Source</th> -->
          <th class="p-3 text-left">Date & Time</th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="log in logs" :key="log.id" class="border-b">
          <td class="p-3">{{ log.document }}</td>
          <td class="p-3">{{ log.user }}</td>
          <td class="p-3">{{ log.action }}</td>
          <!-- <td class="p-3">{{ log.source }}</td> -->
          <td class="p-3">{{ log.accessed_at }}</td>
        </tr>
      </tbody>
    </table>

    <div v-if="!loading && !logs.length" class="text-gray-600 mt-4">
      No logs available.
    </div>
  </div>
</template>
