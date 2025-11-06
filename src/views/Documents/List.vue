<script setup>
    import { ref } from 'vue'
    const docs = ref([
    { id: 1, title: 'Student Handbook.pdf', uploaded_by: 'Admin', created_at: '2025-10-20' },
    { id: 2, title: 'Data Privacy Policy.docx', uploaded_by: 'Admin', created_at: '2025-10-18' }
    ])
</script>

<template>
    <div>
        <div class="flex justify-between items-center mb-4">
            <h1 class="text-xl font-semibold text-dns_dark">Documents</h1>
            <router-link to="/upload" class="px-4 py-2 bg-dns_dark text-white rounded">Upload</router-link>
        </div>

        <div class="bg-white p-4 rounded shadow">
            <table class="min-w-full">
                <thead>
                    <tr class="text-left text-sm text-gray-600">
                    <th class="p-2">Title</th>
                    <th class="p-2">Uploaded By</th>
                    <th class="p-2">Date</th>
                    <th class="p-2">Actions</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="doc in docs" :key="doc.id" class="border-t">
                    <td class="p-2">{{ doc.title }}</td>
                    <td class="p-2">{{ doc.uploaded_by }}</td>
                    <td class="p-2">{{ doc.created_at }}</td>
                    <td class="p-2"><button class="px-2 py-1 bg-dns_green text-white rounded">View</button></td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>


