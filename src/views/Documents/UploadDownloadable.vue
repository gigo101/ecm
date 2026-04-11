<script setup>
import { ref, computed, onUnmounted } from 'vue'
import api from "@/api"
import { useRouter } from "vue-router"
import { useToast } from "vue-toastification"

const router = useRouter()
const toast = useToast()

const selectedFile = ref(null)
const previewUrl = ref(null)
const loading = ref(false)

// Detect file type
const isPDF = computed(() => selectedFile.value?.type === "application/pdf")
const isImage = computed(() => selectedFile.value?.type?.startsWith("image/"))

// Handle file selection
function handleFileChange(event) {
  const file = event.target.files[0]
  if (!file) return

  selectedFile.value = file

  // Clean old preview
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value)
  }

  previewUrl.value = URL.createObjectURL(file)
}

// Remove file
function removeFile() {
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value)
  }

  selectedFile.value = null
  previewUrl.value = null
}

// Upload
async function uploadFile() {
  if (!selectedFile.value) {
    toast.error("Select a file first")
    return
  }

  const formData = new FormData()
  formData.append("file", selectedFile.value)

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

// Cleanup
onUnmounted(() => {
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
})
</script>

<template>
  <div class="flex justify-center p-10">

    <div class="w-full max-w-5xl bg-white shadow-xl rounded-xl border border-gray-200 p-8">

      <!-- Header -->
      <h1 class="text-2xl font-semibold text-dns_dark mb-6">
        Upload Downloadable Form
      </h1>

      <form @submit.prevent="uploadFile">

        <!-- FILE UPLOAD -->
        <div class="mb-6">
          <label class="block text-sm font-medium mb-2">
            Select File
          </label>

          <div class="space-y-3">

            <!-- HIDDEN INPUT -->
            <input
              type="file"
              ref="fileInput"
              class="hidden"
              @change="handleFileChange"
            />

            <!-- BUTTON -->
            <button
              type="button"
              @click="$refs.fileInput.click()"
              class="flex items-center gap-2 px-4 py-2 bg-green-700 hover:bg-green-800 text-white rounded-lg shadow"
            >
              <i class="pi pi-upload"></i>
              Choose File
            </button>

            <!-- FILE NAME -->
            <p class="text-sm text-gray-600">
              {{ selectedFile?.name || "No file selected" }}
            </p>

            <!-- PREVIEW -->
            <div v-if="selectedFile" class="border rounded-lg p-4 bg-gray-50 space-y-3">

              <div class="flex justify-between items-center">
                <span class="font-medium">{{ selectedFile.name }}</span>

                <button
                  type="button"
                  @click="removeFile"
                  class="text-red-600 text-sm hover:underline"
                >
                  Remove
                </button>
              </div>

              <!-- PDF -->
              <iframe
                v-if="isPDF"
                :src="previewUrl"
                class="w-full h-[400px] border rounded"
              />

              <!-- IMAGE -->
              <img
                v-else-if="isImage"
                :src="previewUrl"
                class="max-h-[400px] mx-auto rounded shadow"
              />

              <!-- OTHER -->
              <div v-else class="text-gray-500 text-sm">
                Preview not available for this file type.
              </div>

            </div>

          </div>
        </div>

        <!-- UPLOAD BUTTON -->
        <div class="flex justify-start gap-2">
          <button
            type="submit"
            :disabled="loading"
            class="px-6 py-3 bg-green-700 text-white rounded-lg hover:bg-green-800 transition disabled:opacity-50"
          >
            {{ loading ? "Uploading..." : "Upload" }}
          </button>
          <button
              @click="router.push('/documents/downloadable')"
              class="px-6 py-3 bg-gray-300 rounded-lg hover:bg-gray-400 transition"
            >
              Cancel
          </button>
        </div>

      </form>

    </div>

  </div>
</template>