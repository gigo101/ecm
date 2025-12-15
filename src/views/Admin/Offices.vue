<script setup>
import { ref, onMounted } from "vue";
import api from "@/api";
import { useToast } from "vue-toastification";

const toast = useToast(); // ✅ REQUIRED

const offices = ref([]);
const officeCode = ref("");
const officeName = ref("");
const error = ref("");

async function loadOffices() {
  const res = await api.get("/admin/offices");
  offices.value = res.data;
}

async function addOffice() {
  error.value = ""; // ✅ clear old error

  if (!officeCode.value || !officeName.value) return;

  const formData = new FormData();
  formData.append("office_code", officeCode.value);
  formData.append("name", officeName.value);

  try {
    await api.post("/admin/offices", formData);

    officeCode.value = "";
    officeName.value = "";
    error.value = "";
    loadOffices();
    toast.success("Office added successfully."); // ✅ now works
  } catch (err) {
    error.value = err.response?.data?.detail || "Failed to add office";
    toast.error(error.value);
  }
}

async function deleteOffice(id) {
  if (!confirm("Delete this office?")) return;
  await api.delete(`/admin/offices/${id}`);
  loadOffices();
  toast.success("Office deleted successfully.");
}

onMounted(loadOffices);
</script>


<template>
  <div class="p-8">
    <h1 class="text-2xl font-bold mb-6">Offices Management</h1>

    <div class="flex gap-3 mb-4">
      <input
        v-model="officeCode"
        placeholder="Office Code"
        class="border p-3 rounded w-32"
      />
      <input
        v-model="officeName"
        placeholder="Office Name"
        class="border p-3 rounded w-full"
      />
      <button
        @click="addOffice"
        class="bg-green-700 text-white px-6 rounded"
      >
        Add
      </button>
    </div>

    <p v-if="error" class="text-red-600 mb-3">{{ error }}</p>

<table class="w-full bg-white rounded shadow">
  <thead class="bg-green-700 text-white">
    <tr>
      <th class="p-3 text-left">Office Code</th>
      <th class="p-3 text-left">Office Name</th>

      <!-- Desktop -->
      <th class="p-3 text-center hidden md:table-cell">Delete</th>

      <!-- Mobile -->
      <th class="p-3 text-center md:hidden">Actions</th>
    </tr>
  </thead>

  <tbody>
    <tr v-for="o in offices" :key="o.id" class="border-b hover:bg-gray-50">
      <td class="p-3 font-semibold">{{ o.office_code }}</td>
      <td class="p-3">{{ o.name }}</td>

      <!-- Desktop -->
      <td class="p-3 text-center hidden md:table-cell">
        <button
          @click="deleteOffice(o.id)"
          class="text-red-600 hover:text-red-800"
          title="Delete office"
        >
          🗑️
        </button>
      </td>

      <!-- Mobile -->
      <td class="p-3 md:hidden text-center">
        <details class="relative inline-block">
          <summary class="cursor-pointer py-1 px-3 bg-gray-200 rounded">⋮</summary>

          <div class="absolute right-0 mt-1 bg-white border shadow rounded w-32 z-20">
            <button
              @click="deleteOffice(o.id)"
              class="block w-full text-left px-3 py-2 hover:bg-red-100 text-red-600"
            >
              🗑️ Delete
            </button>
          </div>
        </details>
      </td>
    </tr>
  </tbody>
</table>

  </div>
</template>
