<template>
  <div v-if="route.path === '/documents' || route.path === '/search' || route.path === '/chat' || route.path === '/admin/users' || route.path ==='/documents/upload' || route.path ==='/dashboard' || route.path === '/change-password' || route.path =='/profile' || route.path =='/users' || route.path=='/admin/positions' || route.path=='/admin/offices' || route.path=='/semantic-search'" class="min-h-screen flex bg-dns_beige">
    <Sidebar />
    <div class="flex-1 flex flex-col">
      <Navbar />
      <main class="p-6">
        <router-view />
      </main>
    </div>
  </div>

  <div v-else class="min-h-screen flex bg-dns_beige">
    <div class="flex-1 flex flex-col">
    <main class="p-6">
    <router-view />

    </main>
    </div>
    </div>
  

</template>

<script setup>
import { useRoute } from 'vue-router'
import Sidebar from '@/layouts/Sidebar.vue'
import Navbar from '@/layouts/Navbar.vue'

const route = useRoute()

</script>
