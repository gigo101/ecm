<script setup>
    import { ref } from 'vue'

    const totalDocs = ref(254)
    const weeklyUploads = ref(12)
    const recent = ref([
    { id: 1, title: 'Student Handbook.pdf' },
    { id: 2, title: 'Data Privacy Policy.docx' },
    { id: 3, title: 'Research Ethics Guidelines.pdf' }
    ])
</script>

<template>
    <div>
        <h1 class="text-2xl font-semibold text-dns_dark mb-6">Dashboard</h1>
        <div class="grid grid-cols-2 gap-6">
            <div class="p-6 bg-green-200 rounded shadow">
                <div class="text-sm text-gray-500">Total Documents</div>
                <div class="text-4xl font-bold text-dns_dark mt-2">{{ totalDocs }}</div>
            </div>
            <div class="p-6 bg-green-200 rounded shadow">
                <div class="text-sm text-gray-500">Uploaded this week</div>
                <div class="text-4xl font-bold text-dns_dark mt-2">{{ weeklyUploads }}</div>
            </div>
        </div>

        <section class="mt-8 grid grid-cols-2 gap-6">
            <div class="bg-white p-6 rounded shadow">
                <h2 class="font-semibold mb-4">Recent Uploads</h2>
                <ul class="list-disc pl-6 text-gray-700">
                <li v-for="doc in recent" :key="doc.id">{{ doc.title }}</li>
                </ul>
            </div>
            <div class="bg-white p-6 rounded shadow flex items-center justify-center">
                <router-link to="/upload" class="p-6 border-2 border-dashed rounded text-dns_dark">Upload Document</router-link>
            </div>
        </section>
    </div>
</template>

