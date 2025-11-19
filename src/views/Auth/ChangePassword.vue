<script setup>
import { ref } from "vue";
import api from "@/api";

const oldPassword = ref("");
const newPassword = ref("");
const confirmPassword = ref("");

const loading = ref(false);
const success = ref("");
const error = ref("");

async function changePassword() {
  error.value = "";
  success.value = "";

  if (newPassword.value !== confirmPassword.value) {
    error.value = "New passwords do not match.";
    return;
  }

  loading.value = true;

  try {
    const res = await api.post("/auth/change-password", {
      old_password: oldPassword.value,
      new_password: newPassword.value,
    });

    success.value = "Password updated successfully.";
    oldPassword.value = "";
    newPassword.value = "";
    confirmPassword.value = "";
  } catch (err) {
    console.error(err);
    error.value = err.response?.data?.detail || "Failed to update password.";
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="p-8 max-w-xl mx-auto">
    <h1 class="text-2xl font-bold mb-4">Change Password</h1>

    <div class="bg-white shadow-xl rounded-xl p-6 space-y-4">
      <input
        type="password"
        v-model="oldPassword"
        placeholder="Current Password"
        class="w-full p-3 border rounded-lg"
      />

      <input
        type="password"
        v-model="newPassword"
        placeholder="New Password"
        class="w-full p-3 border rounded-lg"
      />

      <input
        type="password"
        v-model="confirmPassword"
        placeholder="Confirm New Password"
        class="w-full p-3 border rounded-lg"
      />

      <p v-if="error" class="text-red-600">{{ error }}</p>
      <p v-if="success" class="text-green-600">{{ success }}</p>

      <button
        @click="changePassword"
        :disabled="loading"
        class="bg-green-700 text-white px-4 py-2 rounded-lg w-full"
      >
        Change Password
      </button>
    </div>
  </div>
</template>
