<script setup>
import Sidebar from '@/layouts/Sidebar.vue'
import Navbar from '@/layouts/Navbar.vue'
</script>


<template>
<div class="min-h-screen flex bg-dns_beige">
<Sidebar />
<div class="flex-1 flex flex-col">
<Navbar />
<main class="p-6">
<router-view />
</main>
</div>
</div>
</template>


<style>
/* global styles if needed */
</style>
