<template>
  <div v-if="route.path !== '/login'" class="min-h-screen flex bg-dns_beige">
    <Sidebar />
    <div class="flex-1 flex flex-col">
      <Navbar />
      <main class="p-6">
        <router-view />
      </main>
    </div>
  </div>

  <div v-else class="min-h-screen flex items-center justify-center bg-dns_beige">
    <router-view />
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'
import Sidebar from '@/layouts/Sidebar.vue'
import Navbar from '@/layouts/Navbar.vue'

const route = useRoute()
</script>
