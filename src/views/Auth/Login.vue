<template>
  <div class="min-h-screen w-full flex items-center justify-center bg-green-900/70 bg-blend-overlay bg-[url('/images/bg-building.jpg')] bg-cover bg-center bg-no-repeat">
    <div class="bg-white/90 backdrop-blur-md p-8 rounded-2xl shadow-lg w-full max-w-md mx-4">
      <div class="flex flex-col items-center">
        <h2 class="text-2xl font-bold mb-6 text-green-800">Sign In</h2>
      </div>

      <form @submit.prevent="handleLogin" class="space-y-4">
        <input
          v-model="email"
          type="email"
          placeholder="Email address"
          class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
        />
        <input
          v-model="password"
          type="password"
          placeholder="Password"
          class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
        />

        <button
          type="submit"
          class="w-full bg-green-700 hover:bg-green-800 text-white py-3 rounded-lg transition"
          :disabled="loading"
        >
          <span v-if="!loading">Sign In</span>
          <span v-else>Signing in...</span>
        </button>
      </form>

      <p class="text-center text-sm text-gray-600 mt-4">
        Don’t have an account?
        <router-link to="/register" class="text-green-700 hover:underline">Register Now</router-link>
      </p>
    </div>
  </div>
</template>
