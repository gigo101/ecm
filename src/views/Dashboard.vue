<script setup>
import { ref, onMounted } from 'vue'
import api from "@/api"
import SharedWithMeWidget from "@/views/dashboard/SharedWithMeWidget.vue"

const totalDocs = ref(0)
const weeklyUploads = ref(0)
const recent = ref([])
const loading = ref(true)

async function loadDashboard() {
  const res = await api.get("/dashboard/stats")

  totalDocs.value = res.data.total_documents
  weeklyUploads.value = res.data.weekly_uploads
  recent.value = res.data.recent

  loading.value = false
}
onMounted(loadDashboard)
</script>

<template>
 <div class="grid grid-cols-1 md:grid-cols-2 gap-6">

  <div class="p-6 bg-green-200 rounded shadow">
    <div class="text-sm text-gray-500">Total Documents</div>
    <div class="text-4xl font-bold text-dns_dark mt-2">
      {{ totalDocs }}
    </div>
  </div>

  <div class="p-6 bg-green-200 rounded shadow">
    <div class="text-sm text-gray-500">Uploaded this week</div>
    <div class="text-4xl font-bold text-dns_dark mt-2">
      {{ weeklyUploads }}
    </div>
  </div>

  <SharedWithMeWidget />

  <div class="bg-white p-6 rounded shadow">
    <div class="text-sm text-gray-500 mb-2">Recent Documents</div>

    <ul class="space-y-1 text-sm">
      <li
        v-for="doc in recent"
        :key="doc.id"
        class="hover:text-green-700 cursor-pointer"
      >
        • {{ doc.title }}
      </li>
    </ul>
  </div>

</div>
</template>

