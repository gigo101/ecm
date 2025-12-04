<script setup>
import { ref } from "vue";
import api from "@/api";
import { useRouter } from "vue-router";

const router = useRouter();
const email = ref(""); // prefill for testing
const password = ref("");       // prefill for testing
const loading = ref(false);
const error = ref("");

// async function handleLogin() {
//   try {
//     loading.value = true;
//     error.value = "";

//     // FastAPI expects "application/x-www-form-urlencoded"
//     const res = await api.post(
//       "/auth/login",
//       new URLSearchParams({
//         username: email.value,
//         password: password.value,
//       }),
//       {
//         headers: { "Content-Type": "application/x-www-form-urlencoded" },
//       }
//     );

//     const token = res.data.access_token;
//     localStorage.setItem("token", token);
//     router.push("/dashboard");
//   } catch (err) {
//     console.error("Login failed:", err);
//     if (err.response && err.response.data && err.response.data.detail) {
//       error.value = err.response.data.detail;
//     } else {
//       error.value = "Invalid email or password";
//     }
//   } finally {
//     loading.value = false;
//   }
// }

async function handleLogin() {
  try {
    const data = new URLSearchParams();
    data.append("username", email.value);
    data.append("password", password.value);

    const response = await api.post("/auth/login", data, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" }
    });

    const token = response.data.access_token;
    localStorage.setItem("token", token);

    // FETCH USER PROFILE HERE
    const user = await api.get("/users/me");
    localStorage.setItem("role", user.data.role);
    localStorage.setItem("name", user.data.name);

    router.push("/documents");
  } catch (err) {
    error.value = "Login failed.";
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
          <input
            v-model="password"
            type="password"
            placeholder="••••••••"
            required
            class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:outline-none transition"
          />
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
</template>
