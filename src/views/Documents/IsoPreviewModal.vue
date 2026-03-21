<script setup>
import { ref, watch } from "vue"
import api from "@/api"

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

      <!-- PDF VIEW -->
      <iframe
        v-if="fileUrl && !isLoading"
        :src="fileUrl"
        class="w-full h-[75vh] border rounded"
      />

    </div>
  </div>
</template>