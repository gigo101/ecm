<script setup>
import { ref, computed, onUnmounted } from "vue";
import { useRouter } from "vue-router";
import { useToast } from "vue-toastification";
import api from "@/api";

const router = useRouter();
const toast = useToast();

const selectedFile = ref(null);
const previewUrl = ref(null);

const description = ref("");
const category = ref("Auto");
const yearApproved = ref(new Date().getFullYear());
const error = ref("");
const loading = ref(false);
const documentType = ref("Public");

// Detect file type
const isPDF = computed(() => selectedFile.value?.type === "application/pdf");
const isImage = computed(() => selectedFile.value?.type.startsWith("image/"));

// Handle file
function handleFileChange(e) {
  const file = e.target.files[0];
  if (!file) return;

  selectedFile.value = file;

  // Revoke old preview
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value);
  }

  previewUrl.value = URL.createObjectURL(file);
}

// Remove file
function removeFile() {
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value);
  }

  selectedFile.value = null;
  previewUrl.value = null;
}

// Upload
async function uploadDocument() {
  error.value = "";

  if (!selectedFile.value) {
    error.value = "Please select a file.";
    return;
  }

  const formData = new FormData();
  formData.append("file", selectedFile.value);
  formData.append("description", description.value);
  formData.append("category", category.value);
  formData.append("year_approved", yearApproved.value);
  formData.append("document_type", documentType.value);

  loading.value = true;

  try {
    await api.post("/documents/upload", formData);

    toast.success("Document uploaded successfully!");

    removeFile();
    description.value = "";
    category.value = "Auto";
    documentType.value = "Public";

    setTimeout(() => router.push("/documents"), 1200);

  } catch (err) {
    error.value = err.response?.data?.detail || "Upload error";
    toast.error(error.value);
  } finally {
    loading.value = false;
  }
}

// Cleanup on destroy
onUnmounted(() => {
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value);
});
</script>


<template>
  <div class="p-8">
    <h1 class="text-2xl font-bold mb-4">Upload Document</h1>

    <div class="bg-white p-6 rounded-xl shadow-lg space-y-4">
      <input
        type="file"
        @change="handleFileChange"
        class="p-2 border rounded w-full"
      />

            <!-- FILE PREVIEW -->
      <div v-if="selectedFile" class="border rounded-lg p-4 bg-gray-50 space-y-3">

        <div class="flex justify-between items-center">
          <span class="font-medium">{{ selectedFile.name }}</span>

          <button
            @click="removeFile"
            class="text-red-600 text-sm"
          >
            Remove
          </button>
        </div>

        <!-- PDF PREVIEW -->
        <iframe
          v-if="isPDF"
          :src="previewUrl"
          class="w-full h-[400px] border rounded"
        />

        <!-- IMAGE PREVIEW -->
        <img
          v-else-if="isImage"
          :src="previewUrl"
          class="max-h-[400px] mx-auto rounded shadow"
        />

        <!-- OTHER FILE -->
        <div v-else class="text-gray-500 text-sm">
          Preview not available for this file type.
        </div>

      </div>


      <textarea
        v-model="description"
        placeholder="Add a description (optional)"
        class="w-full p-3 border rounded-lg"
      ></textarea>

      <!-- <label class="text-sm font-medium text-gray-700">Category</label> -->

      <select
        v-model="category"
        class="w-full p-3 border rounded-lg focus:ring-2 focus:ring-green-500"
      :class="{'hidden': !visible}">
        <option>Auto</option>  
        <option>General</option>
        <option>Administrative</option>
        <option>Academics</option>
        <option>Policies</option>
        <option>Research</option>
      </select>

       <label class="text-sm font-medium text-gray-700">Year Approved</label>

      <input
        type="number"
        v-model="yearApproved"
        min="1900"
        :max="new Date().getFullYear()"
        class="w-full p-3 border rounded-lg focus:ring-2 focus:ring-green-500"
        placeholder="e.g. 2024"
      />


      <label class="text-sm font-medium text-gray-700">Document Type</label>
      <select
        v-model="documentType"
        class="w-full p-3 border rounded-lg focus:ring-2 focus:ring-green-500"
      >
        <option>Public</option>
        <option>Confidential</option>
        <option>Institutional</option>
      </select>

      <button
        @click="uploadDocument"
        :disabled="loading"
        class="bg-green-700 hover:bg-green-800 text-white px-4 py-2 rounded-lg"
      >
        <span v-if="!loading">Upload</span>
        <span v-else>Uploading...</span>
      </button>

      <p v-if="error" class="text-red-600">{{ error }}</p>
    </div>
  </div>
</template>

