<template>
  <div
    v-if="show"
    class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
    @contextmenu.prevent
  >
    <div class="bg-white w-11/12 max-w-5xl p-6 rounded-xl shadow-xl relative">

      <button @click="close" class="absolute top-3 right-3 text-gray-500 hover:text-black">
        ✕
      </button>

      <h2 class="text-xl font-bold mb-2">{{ metadata.filename }}</h2>

      <div v-if="isLoading" class="flex justify-center items-center h-64">
        <span class="text-gray-500 animate-pulse">Loading document...</span>
      </div>

      <div v-else-if="isPDF" class="overflow-auto h-[70vh] border rounded-lg bg-gray-50" @contextmenu.prevent>
        <VuePdfEmbed
          v-if="pdfSource"
          :source="pdfSource"
          class="w-full shadow-md"
          @contextmenu.prevent
        />
      </div>

      <div v-else-if="isText" class="bg-gray-100 p-4 rounded-lg h-[70vh] overflow-auto">
        <pre>{{ extractedText }}</pre>
      </div>

      <div v-else-if="isUnsupported" class="text-red-600 font-medium">
        Cannot preview this file. Download instead.
      </div>

      <div class="text-sm text-gray-600 mt-4 border-t pt-2">
         <p><strong>Uploaded By:</strong> {{ metadata.uploaded_by }} | {{ metadata.uploaded_at }}</p>
      </div>

    </div>
  </div>
</template>


<script setup>
import { ref, watch, onUnmounted } from "vue";
import api from "@/api";


// Essential styles for the library
import VuePdfEmbed from 'vue-pdf-embed';

const props = defineProps({
  show: Boolean,
  docId: Number,
});

const emit = defineEmits(["close"]);

const pdfSource = ref(null); // Changed from fileUrl to pdfSource
const metadata = ref({});
const extractedText = ref("");
const isPDF = ref(false);
const isText = ref(false);
const isUnsupported = ref(false);
const isLoading = ref(false);

watch(() => props.docId, async (id) => {
  if (!id) return;
  
  // Reset states
  pdfSource.value = null; 
  isLoading.value = true;

  try {
    // 1. Fetch metadata
    const metaRes = await api.get(`/documents/details/${id}`);
    metadata.value = metaRes.data;

    // Determine file type
    const ext = metadata.value.filename.split(".").pop().toLowerCase();
    isPDF.value = ext === "pdf";
    isText.value = ["txt", "md"].includes(ext);
    isUnsupported.value = !isPDF.value && !isText.value;

    // 2. Handle PDF Loading (The Fix)
    if (isPDF.value) {
      // Fetch the actual file content as a BLOB using your secure API instance
      const response = await api.get(`/documents/preview/${id}`, {
        responseType: 'blob' // <--- CRITICAL: Tells axios to handle binary data
      });

      // Create a temporary local URL for the PDF blob
      const blob = new Blob([response.data], { type: 'application/pdf' });
      pdfSource.value = URL.createObjectURL(blob);
    }

    // 3. Load text preview (for OCR text files)
    if (isText.value) {
      const textRes = await api.get(`/documents/text/${id}`);
      extractedText.value = textRes.data.text;
    }
    
  } catch (error) {
    console.error("Error loading document:", error);
    alert("Failed to load document. Please check your permissions.");
  } finally {
    isLoading.value = false;
  }
});

// Clean up the object URL to avoid memory leaks
onUnmounted(() => {
  if (pdfSource.value) {
    URL.revokeObjectURL(pdfSource.value);
  }
});

function close() {
  emit("close");
}
</script>

<style>
/* Optional animations */
</style>
