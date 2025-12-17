<template>
  <div 
    v-if="show"
    class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
    @contextmenu.prevent
  >
    <div class="bg-white w-11/12 max-w-5xl max-h-[90vh] flex flex-col p-6 rounded-xl shadow-xl relative">

      <!-- Close -->
      <button
        @click="close"
        class="absolute top-3 right-3 text-gray-500 hover:text-black"
      >
        ✕
      </button>

      <!-- Filename -->
      <h2 class="text-xl font-bold mb-2 flex-shrink-0">
        {{ metadata.filename || "Document Preview" }}
      </h2>

      <div class="flex-1 overflow-y-auto pr-2">
      <!-- Loading -->
      <div v-if="isLoading" class="flex justify-center items-center h-64">
        <span class="text-gray-500 animate-pulse">
          Loading document...
        </span>
      </div>

      <!-- PDF Preview -->
      <div
        v-else-if="isPDF"
        class="relative overflow-auto h-[70vh] border rounded-lg bg-gray-50"
        @contextmenu.prevent
      >
        <!-- Watermark -->
        <div
          class="absolute inset-0 flex items-center justify-center pointer-events-none select-none"
        >
          <span
            class="text-gray-300 text-6xl font-bold rotate-[-30deg] opacity-20"
          >
            CONFIDENTIAL
          </span>
        </div>

        <VuePdfEmbed
          v-if="pdfSource"
          :source="pdfSource"
          class="w-full shadow-md"
          @contextmenu.prevent
        />
      </div>

      <!-- Text / OCR Preview -->
      <div
        v-else-if="isText"
        class="bg-gray-100 p-4 rounded-lg h-[70vh] overflow-auto"
      >
        <pre class="text-sm whitespace-pre-wrap">
{{ extractedText }}
        </pre>
      </div>

      <!-- Unsupported -->
      <div v-else-if="isUnsupported" class="text-red-600 font-medium">
        Cannot preview this file. Download instead.
      </div>

      <!-- 🔍 Semantic Highlights -->
      <div
        v-if="highlights.length"
        class="mt-4 bg-yellow-50 border border-yellow-200 rounded-lg p-4"
      >
        <h3 class="font-semibold text-yellow-800 mb-2">
          Relevant Excerpts
        </h3>

        <ul class="space-y-2 text-sm">
          <li
            v-for="(h, index) in highlights"
            :key="index"
            class="bg-white p-3 rounded shadow"
          >
            <span class="bg-yellow-200 px-1">
              {{ h.sentence }}
            </span>
            <div class="text-xs text-gray-500 mt-1">
              Relevance score: {{ h.score }}
            </div>
          </li>
        </ul>
      </div>

      <!-- Metadata Footer -->
      <div class="text-sm text-gray-600 mt-4 border-t pt-2">
        <p>
          <strong>Uploaded By:</strong> {{ metadata.uploaded_by }}
          |
          {{ metadata.uploaded_at }}
        </p>
        <p>
          <strong>Category:</strong> {{ metadata.category }}
          |
          <strong>Type:</strong> {{ metadata.document_type }}
        </p>
      </div>
</div>


    </div>
  </div>
</template>

<script setup>
import { ref, watch, onUnmounted } from "vue";
import api from "@/api";
import VuePdfEmbed from "vue-pdf-embed";

/* Props */
const props = defineProps({
  show: Boolean,
  docId: Number,
  query: {
    type: String,
    default: ""
  }
});

const emit = defineEmits(["close"]);

/* State */
const pdfSource = ref(null);
const metadata = ref({});
const extractedText = ref("");
const highlights = ref([]);

const isPDF = ref(false);
const isText = ref(false);
const isUnsupported = ref(false);
const isLoading = ref(false);

/* Watch document change */
watch(() => props.docId, async (id) => {
  if (!id) return;

  // Reset
  if (pdfSource.value) {
    URL.revokeObjectURL(pdfSource.value);
  }

  pdfSource.value = null;
  extractedText.value = "";
  highlights.value = [];
  isPDF.value = false;
  isText.value = false;
  isUnsupported.value = false;
  isLoading.value = true;

  try {
    // Metadata
    const metaRes = await api.get(`/documents/details/${id}`);
    metadata.value = metaRes.data;

    // Detect type
    const ext = metadata.value.filename.split(".").pop().toLowerCase();
    isPDF.value = ext === "pdf";
    isText.value = ["txt", "md"].includes(ext);
    isUnsupported.value = !isPDF.value && !isText.value;

    // PDF blob
    if (isPDF.value) {
      const res = await api.get(`/documents/preview/${id}`, {
        responseType: "blob"
      });
      const blob = new Blob([res.data], { type: "application/pdf" });
      pdfSource.value = URL.createObjectURL(blob);
    }

    // Text preview
    if (isText.value) {
      const textRes = await api.get(`/documents/text/${id}`);
      extractedText.value = textRes.data.text;
    }

    // Semantic highlights
    if (props.query && props.query.trim()) {
      const highlightRes = await api.get(
        `/documents/highlights/${id}`,
        { params: { query: props.query } }
      );
      highlights.value = highlightRes.data;
    }

  } catch (err) {
    console.error("Preview error:", err);
    alert("Failed to load document.");
  } finally {
    isLoading.value = false;
  }
});

/* Cleanup */
onUnmounted(() => {
  if (pdfSource.value) {
    URL.revokeObjectURL(pdfSource.value);
  }
});

/* Close */
function close() {
  emit("close");
}
</script>

<style scoped>
/* Optional: smooth fade */
</style>
