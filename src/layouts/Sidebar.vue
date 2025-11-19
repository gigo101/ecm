<script setup>
</script>

<template>
    <aside class="w-60 bg-dns_dark text-white min-h-screen p-4">
    <nav class="flex flex-col gap-3">
        <router-link to="/dashboard" class="flex items-center gap-3 p-3 rounded hover:bg-dns_green">
        <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M3 12h18M3 6h18M3 18h18"/></svg>
        Dashboard
        </router-link>
        <router-link to="/documents" class="flex items-center gap-3 p-3 rounded hover:bg-dns_green">Documents</router-link>
        <router-link to="/search" class="flex items-center gap-3 p-3 rounded hover:bg-dns_green">Search</router-link>
        <router-link to="/chat" class="flex items-center gap-3 p-3 rounded hover:bg-dns_green">Chatbot</router-link>
        <router-link to="/admin/users" class="flex items-center gap-3 p-3 rounded hover:bg-dns_green">Admin</router-link>
    </nav>
    </aside>
</template>