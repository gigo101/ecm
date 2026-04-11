<script setup>
import { ref } from "vue";
import api from "@/api";
import { useRouter } from "vue-router";
import bgImage from "@/assets/img/bg-1.jpg"
const router = useRouter();
const email = ref(""); // prefill for testing
const password = ref("");       // prefill for testing
const loading = ref(false);
const error = ref("");

const showPassword = ref(false);
const showConfirmPassword = ref(false);

async function handleLogin() {
  try {
    loading.value = true;
    error.value = "";

    const data = new URLSearchParams();
    data.append("username", email.value);
    data.append("password", password.value);

    const response = await api.post("/auth/login", data, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" }
    });

    const token = response.data.access_token;
    localStorage.setItem("token", token);

    // ✅ set globally
    api.defaults.headers.common["Authorization"] = `Bearer ${token}`;

    const user = await api.get("/users/me");
    
    localStorage.setItem("role", user.data.role);
    localStorage.setItem("name", user.data.name);

    router.push("/dashboard");

  } catch (err) {
    console.error("Login error:", err);

    const backendMessage = err.response?.data?.detail;

    if (backendMessage) {
      error.value = backendMessage;
    } else {
      error.value = "Login failed.";
    }

  } finally {
    loading.value = false;
  }
}


</script>

<template>
<div
  class="h-screen w-screen flex items-center justify-center bg-cover bg-center bg-no-repeat relative overflow-hidden"
  :style="{ backgroundImage: `url(${bgImage})` }"
>
    <!-- OVERLAY -->
  <div class="absolute inset-0 bg-green-900/70"></div>
    <div
      class="bg-white/80 backdrop-blur-lg p-10 rounded-3xl shadow-2xl w-full max-w-lg transition transform hover:scale-[1.01]"
    >

      <!-- CONTENT -->

    
    <div class="bg-white/80 backdrop-blur-lg p-10 rounded-3xl shadow-2xl w-full max-w-lg">
      <!-- your existing login content -->
       <div class="flex flex-col items-center mb-10 text-center">
  <!-- APPLICATION TITLE -->
  <h1 class="text-2xl font-extrabold text-green-900 tracking-wide uppercase">
    Enterprise Content Management System
  </h1>

  <div class="w-16 h-1 bg-green-700 rounded-full my-4"></div>

  <!-- PAGE TITLE -->
  <h2 class="text-3xl font-bold text-green-800 tracking-tight">
    Welcome Back
  </h2>

  <p class="text-gray-600 text-sm mt-2">
    Sign in to manage your documents
  </p>
</div>


      <form @submit.prevent="handleLogin" class="space-y-5">
        <div>
          <label class="block text-gray-700 mb-2 text-sm font-medium">
            Email Address
          </label>
          <input
            v-model="email"
            type="email"
            placeholder="email@example.com"
            required
            class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:outline-none transition"
          />
        </div>

        <div>
          <label class="block text-gray-700 mb-2 text-sm font-medium">
            Password
          </label>
            <div class="relative">
            <input
              :type="showPassword ? 'text' : 'password'"
              v-model="password"
              required
              class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:outline-none transition"
            />

            <button
              type="button"
              @click="showPassword = !showPassword"
              class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
            >
              <i :class="showPassword ? 'pi pi-eye-slash' : 'pi pi-eye'"></i>
            </button>
          </div>
        </div>

        <div v-if="error" class="text-red-600 text-sm text-center">
          {{ error }}
        </div>

        <button
          type="submit"
          class="w-full bg-green-700 hover:bg-green-800 text-white font-semibold py-3 rounded-lg shadow-lg transition disabled:opacity-70"
          :disabled="loading"
        >
          <span v-if="!loading">Sign In</span>
          <span v-else>Signing in...</span>
        </button>
      </form>

      <p class="text-center text-sm text-gray-600 mt-6">
        Don’t have an account?
        <router-link
          to="/register"
          class="text-green-700 font-medium hover:underline"
        >
          Register Now
        </router-link>
      </p>
    </div>

    </div>

  </div>


</template>
