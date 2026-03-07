<script setup>
import { ref, onMounted } from "vue"
import api from "@/api"
import { useToast } from "vue-toastification"

const toast = useToast()

const requests = ref([])
const loading = ref(true)
const error = ref("")

const role = ref(localStorage.getItem("role"))

/* 📥 Load requests depending on role */
async function loadRequests() {
  loading.value = true
  error.value = ""

  try {
    let res

    if (role.value === "Viewer") {
      // viewer sees their own requests
      res = await api.get("/documents/my-download-requests")
    } else {
      // uploader/admin sees requests they must approve
      res = await api.get("/download-requests/pending-for-me")
    }

    requests.value = res.data

  } catch (err) {
    console.error(err)
    error.value = "Failed to load download requests."
    toast.error(error.value)
  } finally {
    loading.value = false
  }
}

/* ⬇ Download approved document */
function downloadDocument(docId) {
  const token = localStorage.getItem("token")

  if (!token) {
    toast.error("Not authenticated")
    return
  }

   const baseUrl = import.meta.env.VITE_API_URL;

  const url =
    `${baseUrl}/documents/download/${docId}?token=${token}`

  window.location.href = url

  // refresh list after download
  setTimeout(loadRequests, 800)
}

/* ✅ Approve request */
async function approveRequest(id) {
  try {

    await api.put(`/download-requests/${id}?status=APPROVED`)

    toast.success("Request approved")

    loadRequests()

  } catch (err) {
    console.error(err)
    toast.error("Failed to approve request")
  }
}

/* ❌ Reject request */
async function rejectRequest(id) {
  try {

    await api.put(`/download-requests/${id}?status=REJECTED`)

    toast.success("Request rejected")

    loadRequests()

  } catch (err) {
    console.error(err)
    toast.error("Failed to reject request")
  }
}

/* 🎨 Status color helper */
function statusClass(status) {
  return {
    PENDING: "text-yellow-600",
    APPROVED: "text-green-600",
    REJECTED: "text-red-600"
  }[status] || "text-gray-500"
}

onMounted(loadRequests)
</script>

<template>
  <div class="p-8">

    <h1 class="text-2xl font-semibold mb-6">
      Download Requests
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
          <th class="p-3 text-left">Requester</th>
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
            {{ r.requester_email || "—" }}
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

          <!-- ACTION COLUMN -->
          <td class="p-3 text-center">

            <!-- Viewer Download -->
            <button
              v-if="role === 'Viewer' && r.status === 'APPROVED'"
              @click="downloadDocument(r.document_id)"
              class="px-4 py-2 bg-green-700 text-white rounded hover:bg-green-800"
            >
              Download
            </button>

            <!-- Approve / Reject for uploader/admin -->
            <div
              v-else-if="role !== 'Viewer' && r.status === 'PENDING'"
              class="flex justify-center gap-2"
            >
              <button
                @click="approveRequest(r.id)"
                class="px-3 py-1 bg-green-600 text-white rounded"
              >
                Approve
              </button>

              <button
                @click="rejectRequest(r.id)"
                class="px-3 py-1 bg-red-600 text-white rounded"
              >
                Reject
              </button>
            </div>

            <span v-else class="text-gray-400">
              —
            </span>

          </td>

        </tr>
      </tbody>
    </table>

  </div>
</template>