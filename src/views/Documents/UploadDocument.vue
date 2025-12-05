<script setup>
import { ref } from "vue";
import api from "@/api";

const selectedFile = ref(null);
const description = ref("");
const category = ref("General");
const success = ref("");
const error = ref("");
const loading = ref(false);

function handleFileChange(e) {
  selectedFile.value = e.target.files[0];
}

async function uploadDocument() {
  error.value = "";
  success.value = "";

  if (!selectedFile.value) {
    error.value = "Please select a file.";
    return;
  }

  const formData = new FormData();
  formData.append("file", selectedFile.value);
  formData.append("description", description.value);
  formData.append("category", category.value);

  loading.value = true;

  try {
    const res = await api.post("/documents/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });

    success.value = "Document uploaded successfully!";
    selectedFile.value = null;
    description.value = "";
  } catch (err) {
    console.error("Upload failed:", err);
    error.value = err.response?.data?.detail || "Upload error";
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="p-8">
    <h1 class="text-2xl font-bold mb-4">Upload Document</h1>

    <div class="bg-white p-6 rounded-xl shadow-lg space-y-4">
      <input type="file" @change="handleFileChange" class="p-2 border rounded w-full" />

      <textarea
        v-model="description"
        placeholder="Add a description (optional)"
        class="w-full p-3 border rounded-lg"
      ></textarea>
      <label class="text-sm font-medium text-gray-700">Category</label>
      <select
        v-model="category"
        placeholder="Select Category"
        class="w-full p-3 border rounded-lg focus:ring-2 focus:ring-green-500"
      >
        <option>General</option>
        <option>Administrative</option>
        <option>Finance</option>
        <option>HR</option>
        <option>Procurement</option>
        <option>Research</option>
      </select>

      <button
        @click="uploadDocument"
        :disabled="loading"
        class="bg-green-700 hover:bg-green-800 text-white px-4 py-2 rounded-lg"
      >
        <span v-if="!loading">Upload</span>
        <span v-else>Uploading...</span>
      </button>

      <p v-if="success" class="text-green-600">{{ success }}</p>
      <p v-if="error" class="text-red-600">{{ error }}</p>
    </div>
  </div>
</template>
