<script setup>
    import { ref } from 'vue'
    const q = ref('')
    const messages = ref([
    { sender: 'bot', text: 'Hi — ask me about documents or policies.' }
    ])

    function send() {
    if (!q.value) return
    messages.value.push({ sender: 'user', text: q.value })
    // placeholder bot reply
    messages.value.push({ sender: 'bot', text: 'I found this in Student Handbook: ...' })
    q.value = ''
    }
</script>

<template>
    <div class="max-w-2xl">
        <h1 class="text-xl font-semibold text-dns_dark mb-4">Chatbot</h1>
        <div class="bg-white p-4 rounded shadow h-96 overflow-auto mb-4">
            <div v-for="(m, i) in messages" :key="i" :class="m.sender === 'user' ? 'text-right' : 'text-left'">
                <div :class="['inline-block p-2 rounded', m.sender === 'user' ? 'bg-dns_dark text-white' : 'bg-gray-100']">{{ m.text }}</div>
            </div>
        </div>
        <div class="flex gap-2">
            <input v-model="q" class="flex-1 border p-2 rounded" @keyup.enter="send" />
            <button @click="send" class="px-4 py-2 bg-dns_dark text-white rounded">Send</button>
        </div>
    </div>
</template>


