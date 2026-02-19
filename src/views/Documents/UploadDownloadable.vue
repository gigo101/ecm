<script setup>
import { ref } from "vue"
import api from "@/api"
import { useRouter } from "vue-router"
import { useToast } from "vue-toastification"

const router = useRouter()
const toast = useToast()

const file = ref(null)
const loading = ref(false)

function handleFile(e) {
  file.value = e.target.files[0]
}

async function uploadFile() {
  if (!file.value) {
    toast.error("Select a file first")
    return
  }

  const formData = new FormData()
  formData.append("file", file.value)

  loading.value = true

  try {
    await api.post("/downloadables/upload", formData)

    toast.success("Uploaded successfully")
    router.push("/documents/downloadable")

  } catch {
    toast.error("Upload failed")
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="flex justify-center p-10">

    <div class="w-full max-w-2xl bg-white shadow-xl rounded-xl border border-gray-200 p-8">

      <!-- Header -->
      <h1 class="text-2xl font-semibold text-dns_dark mb-6">
        Upload Downloadable Form
      </h1>

      <form @submit.prevent="uploadFile">

        <!-- File Upload -->
        <div class="mb-6">
          <label class="block text-sm font-medium mb-2">
            Select File
          </label>

          <input
            type="file"
            @change="handleFile"
            class="w-full border border-gray-300 p-3 rounded-lg
                   focus:ring-2 focus:ring-green-600 focus:outline-none"
          />
        </div>

        <!-- Upload Button -->
        <div class="flex justify-end">
          <button
            type="submit"
            :disabled="loading"
            class="px-6 py-3 bg-green-700 text-white rounded-lg
                   hover:bg-green-800 transition disabled:opacity-50"
          >
            {{ loading ? "Uploading..." : "Upload" }}
          </button>
        </div>

      </form>

    </div>

  </div>
</template>

