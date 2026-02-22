<script setup>
import { ref, onMounted } from "vue"
import { useRouter } from "vue-router"
import api from "@/api"

const favorites = ref([])
const loading = ref(true)
const router = useRouter()

async function loadFavorites() {
  try {
    const res = await api.get("/documents/favorites")

    // show top 5 only
    favorites.value = res.data.slice(0, 5)

  } finally {
    loading.value = false
  }
}

onMounted(loadFavorites)
</script>

<template>
  <div class="bg-white shadow rounded-lg p-5">

    <h2 class="text-lg font-semibold mb-3 text-dns_dark">
      ⭐ My Favorites
    </h2>

    <div v-if="loading" class="text-sm text-gray-500">
      Loading...
    </div>

    <div v-else>

      <ul class="space-y-2 text-sm">

        <li
          v-for="doc in favorites"
          :key="doc.id"
          class="hover:text-green-700 cursor-pointer"
          @click="router.push('/documents/favorites')"
        >
          • {{ doc.filename }}
        </li>

        <li v-if="favorites.length === 0" class="text-gray-500">
          No favorite documents yet.
        </li>

      </ul>

      <button
        v-if="favorites.length"
        @click="router.push('/documents/favorites')"
        class="mt-3 text-xs text-green-700 hover:underline"
      >
        View All
      </button>

    </div>

  </div>
</template>