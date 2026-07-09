<template>
  <div class="flex h-screen bg-gray-100">

    <!-- Sidebar -->
    <Sidebar />

    <!-- Main Content -->
    <div class="flex flex-col flex-1 overflow-hidden">

      <!-- Navbar -->
      <Navbar />

      <!-- Page Content -->
      <main
        class="flex-1 overflow-y-auto p-6 bg-gray-100"
      >
        <slot />
      </main>

    </div>

  </div>
</template>

<script setup>
import Sidebar from "@/layouts/Sidebar.vue"
import Navbar from "@/layouts/Navbar.vue"
</script>