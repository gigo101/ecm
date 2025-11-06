<script setup>
    import { ref } from 'vue'
    import axios from 'axios'
    import { useRouter } from 'vue-router'
    const router = useRouter()
    const username = ref('')
    const password = ref('')

    async function login() {
        // call backend /login
        try {
        const res = await axios.post('http://localhost:3000/login', { username: username.value, password: password.value })
        localStorage.setItem('token', res.data.access_token)
        router.push('/')
        } catch (e) {
        alert('Login failed')
        }
    }
</script>

<template>
    <div class="max-w-md mx-auto">
        <h1 class="text-xl font-semibold text-dns_dark mb-4">Login</h1>
        <form @submit.prevent="login">
            <div class="mb-3">
                <input v-model="username" placeholder="Username" class="w-full border p-2 rounded" />
            </div>
            <div class="mb-3">
                <input type="password" v-model="password" placeholder="Password" class="w-full border p-2 rounded" />
            </div>
            <button class="px-4 py-2 bg-dns_dark text-white rounded">Login</button>
        </form>
    </div>
</template>

