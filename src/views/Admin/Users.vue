<template>
<div>
<h1 class="text-xl font-semibold text-dns_dark mb-4">User Management</h1>
<div class="bg-white p-4 rounded shadow">
<table class="min-w-full">
<thead>
<tr class="text-left text-sm text-gray-600"><th class="p-2">Username</th><th class="p-2">Role</th><th class="p-2">Actions</th></tr>
</thead>
<tbody>
<tr v-for="u in users" :key="u.id" class="border-t"><td class="p-2">{{ u.username }}</td><td class="p-2">{{ u.role }}</td><td class="p-2"><button class="px-2 py-1 bg-red-500 text-white rounded">Delete</button></td></tr>
</tbody>
</table>
</div>
</div>
</template>

<script setup>
import { ref } from 'vue'
const users = ref([
{ id: 1, username: 'admin', role: 'admin' },
{ id: 2, username: 'faculty1', role: 'faculty' }
])
</script>
