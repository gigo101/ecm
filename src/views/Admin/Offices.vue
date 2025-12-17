<script setup>
import { ref, onMounted } from "vue";
import api from "@/api";
import { useToast } from "vue-toastification";

const toast = useToast(); // ✅ REQUIRED

const offices = ref([]);
const officeCode = ref("");
const officeName = ref("");
const error = ref("");

const showEditModal = ref(false);

const editOffice = ref({
  id: null,
  office_code: "",
  name: "",
});

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



function openEditModal(office) {
  editOffice.value = { ...office };
  showEditModal.value = true;
}

async function updateOffice() {
  try {
    const formData = new FormData();
    formData.append("office_code", editOffice.value.office_code);
    formData.append("name", editOffice.value.name);

    await api.put(`/admin/offices/${editOffice.value.id}`, formData);

    toast.success("Office updated successfully.");
    showEditModal.value = false;
    loadOffices();
  } catch (err) {
    toast.error(
      err.response?.data?.detail || "Failed to update office."
    );
  }
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
      <th class="p-3 text-center hidden md:table-cell">Edit</th>
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
    @click="openEditModal(o)"
    class="text-blue-600 hover:text-blue-800"
    title="Edit office"
  >
    ✏️
  </button>
  
</td>
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
  @click="openEditModal(o)"
  class="block w-full text-left px-3 py-2 hover:bg-gray-100"
>
  ✏️ Edit
</button>

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
<div
  v-if="showEditModal"
  class="fixed inset-0 bg-black/40 flex items-center justify-center"
>
  <div class="bg-white p-6 rounded-lg w-96 shadow-lg">
    <h2 class="text-xl font-semibold mb-4">Edit Office</h2>

    <input
      v-model="editOffice.office_code"
      class="w-full border p-2 mb-3"
      placeholder="Office Code"
    />

    <input
      v-model="editOffice.name"
      class="w-full border p-2 mb-4"
      placeholder="Office Name"
    />

    <div class="flex justify-end gap-2">
      <button
        @click="showEditModal = false"
        class="px-4 py-2 bg-gray-300 rounded"
      >
        Cancel
      </button>
      <button
        @click="updateOffice"
        class="px-4 py-2 bg-green-700 text-white rounded"
      >
        Save
      </button>
    </div>
  </div>
</div>

  </div>
</template>
