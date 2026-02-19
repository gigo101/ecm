<script setup>
import { ref, watch } from "vue"
import api from "@/api"

const props = defineProps({
  show: Boolean,
  fileId: Number
})

const emit = defineEmits(["close"])

const fileUrl = ref("")
const loading = ref(false)
const error = ref("")

const isPdf = ref(false)
const isImage = ref(false)
const isOffice = ref(false)
const officeUrl = ref("")

watch(() => props.show, async (val) => {
  if (val && props.fileId) {
    await fetchPreview()
  }
})

async function fetchPreview() {
  loading.value = true
  error.value = ""

  try {
    const token = localStorage.getItem("token")

    const res = await api.get(
      `/downloadables/preview/${props.fileId}?token=${token}`,
      { responseType: "blob" }
    )

    const mime = res.headers["content-type"]

    const blob = new Blob([res.data], { type: mime })
    fileUrl.value = URL.createObjectURL(blob)

    isPdf.value = mime.includes("pdf")
    isImage.value = mime.startsWith("image")

    isOffice.value =
      mime.includes("word") ||
      mime.includes("excel") ||
      mime.includes("powerpoint") ||
      mime.includes("officedocument")

    if (isOffice.value) {
      officeUrl.value =
        "https://view.officeapps.live.com/op/embed.aspx?src=" +
        encodeURIComponent(fileUrl.value)
    }

  } catch (err) {
    console.error(err)
    error.value = "Failed to load preview"
  } finally {
    loading.value = false
  }
}

function downloadFile() {
  const token = localStorage.getItem("token")

  window.open(
    `http://127.0.0.1:8000/downloadables/download/${props.fileId}?token=${token}`,
    "_blank"
  )
}

</script>

<template>
  <div v-if="show" class="fixed inset-0 bg-black/50 flex justify-center items-center z-50">

    <div class="bg-white w-11/12 max-w-5xl rounded-lg shadow-lg p-4 relative">

<div class="absolute top-3 right-3 flex gap-2">

  <!-- DOWNLOAD -->
  <button
    @click="downloadFile"
    class="bg-green-600 text-white px-4 py-1.5 rounded hover:bg-green-700 text-sm"
  >
    Download
  </button>

  <!-- CLOSE -->
  <button
    @click="$emit('close')"
    class="text-xl px-2"
  >
    ✕
  </button>

</div>


      <div v-if="loading" class="text-center py-10">Loading preview...</div>
      <div v-else-if="error" class="text-red-600 text-center py-10">{{ error }}</div>

      <iframe v-else-if="isPdf" :src="fileUrl" class="w-full h-[80vh]" />
      <img v-else-if="isImage" :src="fileUrl" class="max-h-[80vh] mx-auto" />
      <iframe v-else-if="isOffice" :src="officeUrl" class="w-full h-[80vh]" />

      <div v-else class="text-center py-10 text-red-600">
        Preview not supported for this file type
      </div>

    </div>
  </div>
</template>
