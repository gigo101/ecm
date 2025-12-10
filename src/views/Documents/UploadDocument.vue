<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useToast } from "vue-toastification";
import api from "@/api";

const router = useRouter();
const toast = useToast();

const selectedFile = ref(null);
const description = ref("");
const category = ref("Auto");
const error = ref("");
const loading = ref(false);
const documentType = ref("Public");

function handleFileChange(e) {
  selectedFile.value = e.target.files[0];
}

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
  formData.append("document_type", documentType.value);

  loading.value = true;

  try {
    await api.post("/documents/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });

    //SHOW TOAST
    toast.success("Document uploaded successfully!");

    //RESET FORM
    selectedFile.value = null;
    description.value = "";
    category.value = "Auto";
    documentType.value = "Public";

    //REDIRECT TO /documents AFTER SHORT DELAY
    setTimeout(() => {
      router.push("/documents");
    }, 1200);

  } catch (err) {
    console.error("Upload failed:", err);
    error.value = err.response?.data?.detail || "Upload error";

    toast.error(error.value);
  } finally {
    loading.value = false;
  }
}
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

