<script setup>
import { ref, onMounted } from "vue"
import api from "@/api"
import SharedWithMeWidget from "@/views/dashboard/SharedWithMeWidget.vue"
import FavoritesWidget from "@/views/dashboard/FavoritesWidget.vue"
import UploadActivityChart from "@/views/dashboard/UploadActivityChart.vue"
import DocumentTypePieChart from "@/views/dashboard/DocumentTypePieChart.vue"

const role = ref("")
const totalDocs = ref(0)
const weeklyUploads = ref(0)
const recent = ref([])
const loading = ref(true)
const error = ref("")

async function loadDashboard() {
  loading.value = true
  error.value = ""

  try {
    const res = await api.get("/dashboard/stats")

    role.value = res.data.role
    totalDocs.value = res.data.total_documents
    weeklyUploads.value = res.data.weekly_uploads
    recent.value = res.data.recent

  } catch (err) {
    error.value = "Failed to load dashboard data."
  } finally {
    loading.value = false
  }
}

onMounted(loadDashboard)
</script>

<template>
  <div class="p-8">

    <!-- TITLE -->
    <h1 class="text-2xl font-semibold text-dns_dark mb-6">
      Dashboard
    </h1>

    <!-- LOADING -->
    <div v-if="loading">Loading dashboard...</div>
    <div v-if="error" class="text-red-600">{{ error }}</div>

    <!-- CONTENT -->
    <div v-if="!loading" class="space-y-6">

      <!-- 📊 STAT CARDS -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">

        <!-- TOTAL / PERSONAL COUNT -->
        <div class="p-6 bg-green-200 rounded shadow">
          <div class="text-sm text-gray-500">
            {{
              role === "Admin"
                ? "Total Documents"
                : role === "Uploader"
                ? "My Documents"
                : "Documents Shared With Me"
            }}
          </div>

          <div class="text-4xl font-bold text-dns_dark mt-2">
            {{ totalDocs }}
          </div>
        </div>

        <!-- WEEKLY UPLOADS (ONLY ADMIN & UPLOADER) -->
        <div
          v-if="role === 'Admin' || role === 'Uploader'"
          class="p-6 bg-green-200 rounded shadow"
        >
          <div class="text-sm text-gray-500">
            {{
              role === "Uploader"
                ? "My uploads this week"
                : "Uploaded this week"
            }}
          </div>

          <div class="text-4xl font-bold text-dns_dark mt-2">
            {{ weeklyUploads }}
          </div>
        </div>

      </div>

      <!-- 📄 MAIN GRID -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">

        <!-- 🔔 SHARED WITH ME WIDGET -->
        <SharedWithMeWidget />
        <FavoritesWidget />
        <UploadActivityChart
            v-if="role === 'Admin' || role === 'Uploader'"
        />
        <DocumentTypePieChart
            v-if="role === 'Admin' || role === 'Uploader'"
        />
        <!-- 🕒 RECENT DOCUMENTS -->
        <div class="bg-white p-6 rounded shadow">

          <div class="text-sm text-gray-500 mb-2">
            {{
              role === "Admin"
                ? "Recent Documents"
                : role === "Uploader"
                ? "My Recent Uploads"
                : "Recently Shared With Me"
            }}
          </div>

          <ul class="space-y-2 text-sm">

            <li
              v-for="doc in recent"
              :key="doc.id"
              class="hover:text-green-700 cursor-pointer"
            >
              • {{ doc.title }}
            </li>

            <li v-if="recent.length === 0" class="text-gray-500">
              No documents found.
            </li>

          </ul>

        </div>

      </div>

    </div>

  </div>
</template>