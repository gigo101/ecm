<script setup>
import { ref } from "vue";
import api from "../../api";
import { useRouter } from "vue-router";

const router = useRouter();

const first_name = ref("");
const middle_name = ref("");
const last_name = ref("");
const suffix = ref("");
const position = ref("");
const office = ref("");
const email = ref("");
const password = ref("");
const confirmPassword = ref("");

const loading = ref(false);
const error = ref("");
const success = ref("");

async function handleRegister() {
  error.value = "";
  success.value = "";

  if (password.value !== confirmPassword.value) {
    error.value = "Passwords do not match.";
    return;
  }

  loading.value = true;

  try {
    await api.post("/auth/register", {
      first_name: first_name.value,
      middle_name: middle_name.value,
      last_name: last_name.value,
      suffix: suffix.value,
      position: position.value,
      office: office.value,
      email: email.value,
      password: password.value,
    });

    success.value = "Account successfully created!";
    
    setTimeout(() => router.push("/login"), 2000);

  } catch (err) {
    error.value = err.response?.data?.detail || "Registration failed.";
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div
    class="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-900 via-green-800 to-green-700 bg-cover bg-center"
    style="background-image: url('/images/bg-building.jpg'); background-blend-mode: overlay;"
  >
    <div class="bg-white/80 backdrop-blur-lg p-10 rounded-3xl shadow-2xl w-full max-w-md">

      <h2 class="text-3xl font-extrabold text-green-800 text-center mb-6">Create Account</h2>

      <form @submit.prevent="handleRegister" class="space-y-4">

        <!-- First Name -->
        <div>
          <label class="block text-gray-700 mb-1 text-sm">First Name</label>
          <input v-model="first_name" required class="w-full p-3 border rounded-lg" />
        </div>

         <!-- Middle Name -->
        <div>
          <label class="block text-gray-700 mb-1 text-sm">Middle Name</label>
          <input v-model="middle_name" required class="w-full p-3 border rounded-lg" />
        </div>

        <!-- Last Name -->
        <div>
          <label class="block text-gray-700 mb-1 text-sm">Last Name</label>
          <input v-model="last_name" required class="w-full p-3 border rounded-lg" />
        </div>

        <!-- Suffix -->
        <div>
          <label class="block text-gray-700 mb-1 text-sm">Suffix (optional)</label>
          <input v-model="suffix" placeholder="Jr., III, etc." class="w-full p-3 border rounded-lg" />
        </div>

        <!-- Position -->
        <div>
          <label class="block text-gray-700 mb-1 text-sm">Position</label>
          <input v-model="position" required class="w-full p-3 border rounded-lg" />
        </div>

        <!-- Office -->
        <div>
          <label class="block text-gray-700 mb-1 text-sm">Office</label>
          <input v-model="office" required class="w-full p-3 border rounded-lg" />
        </div>

        <!-- Email -->
        <div>
          <label class="block text-gray-700 mb-1 text-sm">Email</label>
          <input type="email" v-model="email" required class="w-full p-3 border rounded-lg" />
        </div>

        <!-- Password -->
        <div>
          <label class="block text-gray-700 mb-1 text-sm">Password</label>
          <input type="password" v-model="password" required class="w-full p-3 border rounded-lg" />
        </div>

        <!-- Confirm Password -->
        <div>
          <label class="block text-gray-700 mb-1 text-sm">Confirm Password</label>
          <input type="password" v-model="confirmPassword" required class="w-full p-3 border rounded-lg" />
        </div>

        <!-- Error / Success -->
        <div v-if="error" class="text-red-600 text-center text-sm">{{ error }}</div>
        <div v-if="success" class="text-green-700 text-center text-sm font-semibold">{{ success }}</div>

        <!-- Button -->
        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-green-700 hover:bg-green-800 text-white p-3 rounded-lg shadow"
        >
          <span v-if="!loading">Register</span>
          <span v-else>Creating Account...</span>
        </button>

      </form>

      <p class="text-center text-sm text-gray-600 mt-6">
        Already have an account?
        <router-link to="/login" class="text-green-700 hover:underline">Log in</router-link>
      </p>

    </div>
  </div>
</template>
