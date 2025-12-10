<script setup>
    import { ref } from 'vue'
    import axios from 'axios'

    const title = ref('')
    const description = ref('')
    const file = ref(null)

    function onFile(e) { file.value = e.target.files[0] }

    async function submit() {
        if (!file.value) return alert('Please choose a file')
        const fd = new FormData()
        fd.append('title', title.value)
        fd.append('description', description.value)
        fd.append('file', file.value)
        await axios.post('http://localhost:8000/upload', fd)
        alert('Uploaded')

    }
</script>

<template>
    <div class="max-w-2xl">
        <h1 class="text-xl font-semibold text-dns_dark mb-4">Upload Document</h1>
        <form @submit.prevent="submit">
            <div class="mb-4">
                <label class="block text-sm mb-1">Title</label>
                <input v-model="title" class="w-full border p-2 rounded" />
            </div>
            <div class="mb-4">
                <label class="block text-sm mb-1">Description</label>
                <textarea v-model="description" class="w-full border p-2 rounded"></textarea>
            </div>
            <div class="mb-4">
                <label class="block text-sm mb-1">File</label>
                <input type="file" @change="onFile" />
            </div>
            <button class="px-4 py-2 bg-dns_dark text-white rounded">Upload</button>
        </form>
    </div>
</template>
