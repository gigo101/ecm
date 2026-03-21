<script setup>
import { ref } from "vue"
import { useRouter } from "vue-router"
import api from "@/api"
import { useToast } from "vue-toastification"

const router = useRouter()
const toast = useToast()

const file = ref(null)
const uploading = ref(false)

const role = localStorage.getItem("role")

/* 🚫 Protect route */
if (role !== "Admin" && role !== "Uploader") {
  router.push("/")
}

/* Handle file selection */
function handleFileChange(e) {
  file.value = e.target.files[0]
}

/* Upload file */
async function uploadFile() {

  if (!file.value) {
    toast.warning("Please select a file")
    return
  }

  const formData = new FormData()
  formData.append("file", file.value)

  uploading.value = true

  try {

    await api.post("/iso-procedures/upload", formData)

    toast.success("ISO Procedure uploaded successfully 📄")

    router.push("/documents/procedures-manual")

  } catch (err) {

    console.error(err)
    toast.error("Upload failed")

  } finally {

    uploading.value = false

  }

}
</script>

<template>
  <div class="p-8 max-w-lg mx-auto">

    <h1 class="text-2xl font-semibold mb-6">
      Upload ISO Procedure
    </h1>

    <!-- FILE INPUT -->
    <div class="mb-4">
      <input
        type="file"
        @change="handleFileChange"
        class="w-full border p-2 rounded"
      />
    </div>

    <!-- ACTIONS -->
    <div class="flex gap-2">

      <button
        @click="uploadFile"
        :disabled="uploading"
        class="bg-green-700 text-white px-4 py-2 rounded hover:bg-green-800"
      >
        {{ uploading ? "Uploading..." : "Upload" }}
      </button>

      <button
        @click="router.push('/documents/procedures-manual')"
        class="bg-gray-300 px-4 py-2 rounded"
      >
        Cancel
      </button>

    </div>

  </div>
</template>