<script setup>
import { ref, watch } from "vue"
import api from "@/api"
import VuePdfEmbed from "vue-pdf-embed"

const isPDF = ref(false)

function detectType(filename) {
  const ext = filename.split(".").pop().toLowerCase()
  isPDF.value = ext === "pdf"
}

const props = defineProps({
  show: Boolean,
  fileId: Number
})

const emit = defineEmits(["close"])

const fileUrl = ref(null)
const isLoading = ref(false)

/* LOAD FILE */
watch(() => props.fileId, async (id) => {

  if (!id) return

  isLoading.value = true

  try {

    const meta = await api.get(`/iso-procedures/list`)
    const file = meta.data.find(f => f.id === id)

    detectType(file.filename)

    const res = await api.get(`/iso-procedures/preview/${id}`, {
      responseType: "blob"
    })

    fileUrl.value = URL.createObjectURL(res.data)

  } catch (err) {

    console.error(err)
    alert("Failed to load preview")

  } finally {
    isLoading.value = false
  }

})

/* CLOSE */
function close() {
  if (fileUrl.value) {
    URL.revokeObjectURL(fileUrl.value)
  }
  fileUrl.value = null
  emit("close")
}
</script>

<template>
  <div
    v-if="show"
    class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
    @contextmenu.prevent
  >
    <div class="bg-white w-11/12 max-w-5xl p-6 rounded-xl shadow-xl relative">

      <!-- CLOSE -->
      <button
        @click="close"
        class="absolute top-3 right-3 text-gray-500 hover:text-black"
      >
        ✕
      </button>

      <h2 class="text-lg font-semibold mb-4">
        ISO Procedure Preview
      </h2>

      <!-- LOADING -->
      <div v-if="isLoading" class="text-center py-10">
        Loading...
      </div>

      <!-- PDF (NO TOOLBAR) -->
      <div
        v-else-if="isPDF"
        class="h-[75vh] overflow-auto border rounded bg-gray-50 relative"
      >
        <!-- WATERMARK -->
        <div class="absolute inset-0 flex items-center justify-center pointer-events-none">
          <span class="text-gray-300 text-5xl rotate-[-30deg] opacity-20">
            CONFIDENTIAL
          </span>
        </div>

        <VuePdfEmbed
          v-if="fileUrl"
          :source="fileUrl"
          class="w-full"
        />
      </div>

      <!-- IMAGE -->
      <div
        v-else
        class="flex justify-center items-center h-[75vh]"
      >
        <img :src="fileUrl" class="max-h-full max-w-full" />
      </div>

    </div>
  </div>
</template>