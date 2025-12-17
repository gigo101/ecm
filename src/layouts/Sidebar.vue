<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();
const role = ref(localStorage.getItem("role"));
</script>


<template>
  <aside class="w-60 bg-dns_dark text-white min-h-screen p-4">
    <nav class="flex flex-col gap-3">

      <!-- GENERAL -->
      <router-link
        to="/dashboard"
        class="flex items-center gap-3 p-3 rounded hover:bg-dns_green"
      >
        <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M3 12h18M3 6h18M3 18h18" />
        </svg>
        Dashboard
      </router-link>

      <router-link
        to="/documents"
        class="flex items-center gap-3 p-3 rounded hover:bg-dns_green"
      >  <i class="pi pi-file text-dns_light text-lg"></i>
        Documents
      </router-link>
      <router-link
        to="/semantic-search"
        class="flex items-center gap-2 px-4 py-2 hover:bg-dns_green"
        >
        <i class="pi pi-search"></i>
        Semantic Search
      </router-link>

      <!-- ADMIN SECTION -->
      <div v-if="role === 'Admin'" class="mt-6">
        <p class="text-xs uppercase text-gray-300 px-3 mb-2 tracking-wide">
          Administration
        </p>

        <router-link
          to="/users"
          class="flex items-center gap-3 p-3 rounded hover:bg-dns_green"
        >
         <i class="pi pi-user-edit text-dns_light text-lg"></i> User Management
        </router-link>

        <router-link
          to="/admin/offices"
          class="flex items-center gap-3 p-3 rounded hover:bg-dns_green"
        >
        <i class="pi pi-warehouse text-dns_light text-lg"></i>Offices
        </router-link>

        <router-link
          to="/admin/positions"
          class="flex items-center gap-3 p-3 rounded hover:bg-dns_green"
        >
          <i class="pi pi-users text-dns_light text-lg"></i> Positions
        </router-link>
      </div>

    </nav>
  </aside>
</template>
