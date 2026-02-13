<template>
  <div
    v-if="show"
    class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
    @contextmenu.prevent
  >
    <div
      class="bg-white w-11/12 max-w-5xl max-h-[90vh] flex flex-col p-6 rounded-xl shadow-xl relative"
    >
      <!-- CLOSE -->
      <button
        @click="close"
        class="absolute top-3 right-3 text-gray-500 hover:text-black"
      >
        ✕
      </button>

      <!-- HEADER -->
      <div class="flex justify-between items-center mb-3">
        <h2 class="text-xl font-bold">{{ metadata.filename }}</h2>

        <!-- DOWNLOAD -->
        <button
          v-if="canDownload"
          @click="downloadDocument"
          class="bg-green-700 text-white px-4 py-2 rounded hover:bg-green-800"
        >
          Download
        </button>

        <!-- REQUEST DOWNLOAD -->
        <button
          v-else-if="role === 'Viewer'"
          @click="openRequestModal"
          class="bg-yellow-600 text-white px-4 py-2 rounded hover:bg-yellow-700"
        >
          Request Download
        </button>
      </div>

      <!-- BODY -->
      <div class="flex-1 overflow-y-auto pr-2">

        <!-- LOADING -->
        <div v-if="isLoading" class="flex justify-center items-center h-64">
          <span class="text-gray-500 animate-pulse">Loading document...</span>
        </div>

        <!-- PDF -->
        <div
          v-else-if="isPDF"
          class="relative overflow-auto h-[70vh] border rounded-lg bg-gray-50"
        >
          <Watermark />

          <VuePdfEmbed
            v-if="fileUrl"
            :source="fileUrl"
            class="w-full"
          />
        </div>

        <!-- IMAGE PREVIEW -->
        <div
          v-else-if="isImage"
          class="relative flex justify-center items-center bg-gray-50 border rounded-lg h-[70vh]"
        >
          <Watermark />

          <img
            :src="fileUrl"
            class="max-h-full max-w-full rounded shadow"
          />
        </div>

        <!-- TEXT -->
        <div
          v-else-if="isText"
          class="bg-gray-100 p-4 rounded-lg h-[70vh] overflow-auto"
        >
          <pre class="text-sm whitespace-pre-wrap">{{ extractedText }}</pre>
        </div>

        <!-- UNSUPPORTED -->
        <div v-else class="text-red-600 font-medium">
          Cannot preview this file. Download instead.
        </div>

        <!-- 🔍 SEMANTIC HIGHLIGHTS -->
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
              <span class="bg-yellow-200 px-1">{{ h.sentence }}</span>
              <div class="text-xs text-gray-500 mt-1">
                Relevance score: {{ h.score }}
              </div>
            </li>
          </ul>
        </div>

        <!-- METADATA -->
        <div class="text-sm text-gray-600 mt-4 border-t pt-2">
          <p>
            <strong>Uploaded By:</strong> {{ metadata.uploaded_by }} |
            {{ metadata.uploaded_at }}
          </p>
          <p>
            <strong>Category:</strong> {{ metadata.category }} |
            <strong>Type:</strong> {{ metadata.document_type }}
          </p>
        </div>
      </div>

      <!-- REQUEST MODAL -->
      <div
        v-if="showRequestModal"
        class="fixed inset-0 bg-black/40 flex items-center justify-center z-50"
      >
        <div class="bg-white p-6 rounded-lg w-96 shadow-lg">
          <h3 class="text-lg font-semibold mb-3">Request Download</h3>

          <textarea
            v-model="requestReason"
            placeholder="Reason (optional)"
            class="w-full p-2 border rounded mb-4"
          />

          <div class="flex justify-end gap-2">
            <button
              @click="showRequestModal = false"
              class="px-4 py-2 bg-gray-300 rounded"
            >
              Cancel
            </button>

            <button
              @click="submitDownloadRequest"
              class="px-4 py-2 bg-green-700 text-white rounded"
            >
              Submit
            </button>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, watch, onUnmounted, computed } from "vue";
import api from "@/api";
import VuePdfEmbed from "vue-pdf-embed";

/* PROPS */
const props = defineProps({
  show: Boolean,
  docId: Number,
  query: String,
  source: { type: String, default: "LIST" }
});

const emit = defineEmits(["close"]);

/* STATE */
const metadata = ref({});
const fileUrl = ref(null);
const extractedText = ref("");
const highlights = ref([]);

const isPDF = ref(false);
const isImage = ref(false);
const isText = ref(false);
const isLoading = ref(false);

const role = computed(() => localStorage.getItem("role"));

const canDownload = computed(() =>
  ["Admin", "Uploader", "Faculty", "Staff", "Management"].includes(role.value)
);

/* FILE TYPE DETECTION */
function detectType(filename) {
  const ext = filename.split(".").pop().toLowerCase();

  isPDF.value = ext === "pdf";
  isImage.value = ["jpg", "jpeg", "png", "gif", "webp"].includes(ext);
  isText.value = ["txt", "md"].includes(ext);
}

/* LOAD DOCUMENT */
watch(() => props.docId, async (id) => {
  if (!id) return;

  cleanup();

  isLoading.value = true;

  try {
    const metaRes = await api.get(`/documents/details/${id}`);
    metadata.value = metaRes.data;

    detectType(metadata.value.filename);

    if (isPDF.value || isImage.value) {
      const res = await api.get(`/documents/preview/${id}`, {
        responseType: "blob",
        params: { source: props.source }
      });

      fileUrl.value = URL.createObjectURL(res.data);
    }

    if (isText.value) {
      const textRes = await api.get(`/documents/text/${id}`);
      extractedText.value = textRes.data.text;
    }

    if (props.query?.trim()) {
      const highlightRes = await api.get(
        `/documents/highlights/${id}`,
        { params: { query: props.query } }
      );
      highlights.value = highlightRes.data;
    }

  } catch (err) {
    alert("Failed to load document.");
  } finally {
    isLoading.value = false;
  }
});

/* DOWNLOAD */
function downloadDocument() {
  const token = localStorage.getItem("token");
  window.open(
    `http://127.0.0.1:8000/documents/download/${props.docId}?token=${token}`
  );
}

/* REQUEST DOWNLOAD */
const showRequestModal = ref(false);
const requestReason = ref("");

function openRequestModal() {
  showRequestModal.value = true;
}

async function submitDownloadRequest() {
  await api.post(`/documents/${props.docId}/request-download`, {
    reason: requestReason.value
  });

  showRequestModal.value = false;
  requestReason.value = "";
  alert("Request submitted.");
}

/* CLEANUP */
function cleanup() {
  if (fileUrl.value) URL.revokeObjectURL(fileUrl.value);

  fileUrl.value = null;
  extractedText.value = "";
  highlights.value = [];
}

/* CLOSE */
function close() {
  cleanup();
  emit("close");
}

onUnmounted(cleanup);
</script>

<!-- WATERMARK COMPONENT -->
<script>
export default {
  components: {
    Watermark: {
      template: `
        <div class="absolute inset-0 flex items-center justify-center pointer-events-none select-none">
          <span class="text-gray-300 text-6xl font-bold rotate-[-30deg] opacity-20">
            CONFIDENTIAL
          </span>
        </div>
      `
    }
  }
};
</script>
