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
        class="flex items-center gap-2 p-1 rounded hover:bg-dns_green"
      >
        <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M3 12h18M3 6h18M3 18h18" />
        </svg>
        Dashboard
      </router-link>

      <router-link
        to="/documents"
        class="flex items-center gap-2 p-1 rounded hover:bg-dns_green"
      >  <i class="pi pi-file text-dns_light text-lg"></i>
        Documents
      </router-link>
      <router-link
        v-if="role === 'Admin' || role === 'Uploader'"
        to="/documents/my-uploads"
        class="flex items-center gap-2 p-1 rounded hover:bg-dns_green"
      >
        <i class="pi pi-upload text-dns_light text-lg"></i>
       My Uploads
      </router-link>
      <router-link to="/documents/shared" class="flex items-center gap-2 p-1 rounded hover:bg-dns_green">
        <i class="pi pi-file-export text-dns_light text-lg"></i>
        Shared Documents
      </router-link>
      <router-link
        to="/semantic-search"
        class="flex items-center gap-2 p-1 rounded hover:bg-dns_green"
        >
        <i class="pi pi-search"></i>
        Semantic Search
      </router-link>

      <router-link to="/my-download-requests" class="flex items-center gap-2 p-1 rounded hover:bg-dns_green">
        <i class="pi 
          pi-arrow-circle-down"></i> Download Requests
      </router-link>

      <router-link to="/documents/favorites" class="flex items-center gap-2 p-1 rounded hover:bg-dns_green">
        <i class="pi pi-star"></i>
        My Favorites
      </router-link>

      <router-link to="/documents/downloadable" class="flex items-center gap-2 p-1 rounded hover:bg-dns_green">
        <i class="pi pi-align-justify"></i>
         Downloadable Forms
      </router-link>

      <router-link to="/documents/procedures-manual" class="flex items-center gap-2 p-1 rounded hover:bg-dns_green">
        <i class="pi pi-align-justify"></i>
         Procedures Manual
      </router-link>
   

      <!-- ADMIN SECTION -->
      <div v-if="role === 'Admin'">
        <p class="text-xs uppercase text-gray-300 px-3 mb-2 tracking-wide pt-4">
          Administration
        </p>


        <router-link  v-if="role === 'Admin'" to="/admin/download-requests" class="flex items-center gap-2 p-1 rounded hover:bg-dns_green">
            <i class="pi pi-download"></i> Download Requests
        </router-link>

        <router-link
          to="/users"
          class="flex items-center gap-2 p-1 rounded hover:bg-dns_green"
        >
         <i class="pi pi-user-edit"></i> User Management
        </router-link>

        <router-link
          to="/admin/offices"
          class="flex items-center gap-2 p-1 rounded hover:bg-dns_green"
        >
        <i class="pi pi-warehouse"></i>Offices
        </router-link>

        <router-link
          to="/admin/positions"
          class="flex items-center gap-2 p-1 rounded hover:bg-dns_green"
        >
          <i class="pi pi-users"></i> Positions
        </router-link>

        <router-link
          v-if="role === 'Admin'"
          to="/admin/document-logs"
          class="flex items-center gap-2 p-1 rounded hover:bg-dns_green"
        >
        <i class="pi pi-history"></i> Document Logs
        </router-link>

        

      </div>

    </nav>
  </aside>
</template>
