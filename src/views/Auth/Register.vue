<script setup>
import { ref } from "vue";
import api from "../../api";
import { useRouter } from "vue-router";

const router = useRouter();

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
    const res = await api.post("/auth/register", {
      email: email.value,
      password: password.value,
    });

    success.value = "Account created successfully! Redirecting...";
    
    // Redirect after 2 seconds
    setTimeout(() => {
      router.push("/login");
    }, 2000);

  } catch (err) {
    console.error("Registration failed:", err);
    if (err.response?.data?.detail) {
      error.value = err.response.data.detail;
    } else {
      error.value = "Something went wrong during registration.";
    }
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
    <div
      class="bg-white/80 backdrop-blur-lg p-10 rounded-3xl shadow-2xl w-full max-w-md transition transform hover:scale-[1.01]"
    >
      <div class="flex flex-col items-center mb-8">
        <h2 class="text-3xl font-extrabold text-green-800 tracking-tight">
          Create Account
        </h2>
        <p class="text-gray-600 text-sm mt-2">
          Register to access the ECM system
        </p>
      </div>

      <form @submit.prevent="handleRegister" class="space-y-5">
        
        <div>
          <label class="block text-gray-700 mb-2 text-sm font-medium">Email</label>
          <input
            type="email"
            v-model="email"
            required
            placeholder="yourname@example.com"
            class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
          />
        </div>

        <div>
          <label class="block text-gray-700 mb-2 text-sm font-medium">Password</label>
          <input
            type="password"
            v-model="password"
            required
            placeholder="••••••••"
            class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
          />
        </div>

        <div>
          <label class="block text-gray-700 mb-2 text-sm font-medium">Confirm Password</label>
          <input
            type="password"
            v-model="confirmPassword"
            required
            placeholder="••••••••"
            class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
          />
        </div>

        <div v-if="error" class="text-red-600 text-sm text-center">
          {{ error }}
        </div>

        <div v-if="success" class="text-green-700 text-sm text-center font-medium">
          {{ success }}
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-green-700 hover:bg-green-800 text-white font-semibold py-3 rounded-lg shadow-lg transition disabled:opacity-70"
        >
          <span v-if="!loading">Register</span>
          <span v-else>Creating account...</span>
        </button>
      </form>

      <p class="text-center text-sm text-gray-600 mt-6">
        Already have an account?
        <router-link
          to="/login"
          class="text-green-700 font-medium hover:underline"
        >
          Sign In
        </router-link>
      </p>
    </div>
  </div>
</template>
