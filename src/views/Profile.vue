<script setup>
import { ref, onMounted } from "vue";
import api from "@/api";

const name = ref("");
const email = ref("");
const role = ref("");

const loading = ref(true);

async function loadProfile() {
  try {
    const res = await api.get("/users/me");
    name.value = res.data.name;
    email.value = res.data.email;
    role.value = res.data.role;
  } catch (err) {
    console.error("Failed to load profile", err);
  } finally {
    loading.value = false;
  }
}

onMounted(loadProfile);
</script>

<template>
  <div class="p-8 max-w-3xl mx-auto">
    <h1 class="text-3xl font-bold text-dns_dark mb-6">My Profile</h1>

    <div class="bg-white shadow-xl rounded-2xl p-8 space-y-6">

      <div v-if="loading" class="text-center text-gray-500">Loading...</div>

      <template v-else>
        <div class="flex flex-col gap-1">
          <label class="text-gray-500 text-sm">Name</label>
          <div class="text-lg font-semibold">{{ name }}</div>
        </div>

        <div class="flex flex-col gap-1">
          <label class="text-gray-500 text-sm">Email</label>
          <div class="text-lg font-semibold">{{ email }}</div>
        </div>

        <div class="flex flex-col gap-1">
          <label class="text-gray-500 text-sm">Role</label>
          <div class="text-lg font-semibold">{{ role }}</div>
        </div>

        <router-link
          to="/change-password"
          class="inline-block mt-6 px-6 py-2 rounded-lg bg-green-700 text-white hover:bg-green-800"
        >
          Change Password
        </router-link>
      </template>
    </div>
  </div>
</template>
