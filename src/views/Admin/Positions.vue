<script setup>
import { ref, onMounted } from "vue";
import api from "@/api";
import { useToast } from "vue-toastification";

const toast = useToast(); // ✅ REQUIRED

const positions = ref([]);
const newPosition = ref("");
const error = ref("");
const showEditModal = ref(false);

const editPosition = ref({
  id: null,
  name: "",
});

function openEditModal(position) {
  editPosition.value = { ...position };
  showEditModal.value = true;
}

async function updatePosition() {
  try {
    const formData = new FormData();
    formData.append("name", editPosition.value.name);

    await api.put(`/admin/positions/${editPosition.value.id}`, formData);

    toast.success("Position updated successfully.");
    showEditModal.value = false;
    loadPositions();
  } catch (err) {
    toast.error(
      err.response?.data?.detail || "Failed to update position."
    );
  }
}

async function loadPositions() {
  const res = await api.get("/admin/positions");
  positions.value = res.data;
}

async function addPosition() {
  error.value = ""; // ✅ clear old error

  if (!newPosition.value) {
    error.value = "Position name is required.";
    return;
  }

  const formData = new FormData();
  formData.append("name", newPosition.value);

  try {
    await api.post("/admin/positions", formData);

    newPosition.value = "";
    error.value = "";
    loadPositions();
    toast.success("Position added successfully."); // ✅ success toast
  } catch (err) {
    error.value = err.response?.data?.detail || "Failed to add position";
    toast.error(error.value); // ✅ error toast
  }
}

async function deletePosition(id) {
  if (!confirm("Delete this position?")) return;

  try {
    await api.delete(`/admin/positions/${id}`);
    loadPositions();
    toast.success("Position deleted successfully."); // ✅ delete toast
  } catch {
    toast.error("Failed to delete position.");
  }
}

onMounted(loadPositions);
</script>


<template>
  <div class="p-8">
    <h1 class="text-2xl font-bold mb-6">Positions Management</h1>

    <div class="flex gap-3 mb-4">
      <input
        v-model="newPosition"
        placeholder="New position name"
        class="border p-3 rounded w-full"
      />
      <button
        @click="addPosition"
        class="bg-green-700 text-white px-6 rounded"
      >
        Add
      </button>
    </div>

    <p v-if="error" class="text-red-600 mb-3">{{ error }}</p>

    <table class="w-full bg-white rounded shadow">
  <thead class="bg-green-700 text-white">
    <tr>
      <th class="p-3 text-left">Position Name</th>

      <!-- Desktop -->
       <th class="p-3 text-center hidden md:table-cell">Edit</th>
      <th class="p-3 text-center hidden md:table-cell">Delete</th>

      <!-- Mobile -->
      <th class="p-3 text-center md:hidden">Actions</th>
    </tr>
  </thead>

  <tbody>
    <tr v-for="p in positions" :key="p.id" class="border-b hover:bg-gray-50">
      <td class="p-3">{{ p.name }}</td>

      <!-- Desktop -->
       <td class="p-3 text-center hidden md:table-cell">
  <button
    @click="openEditModal(p)"
    class="text-blue-600 hover:text-blue-800"
    title="Edit position"
  >
    ✏️
  </button>
</td>

      <td class="p-3 text-center hidden md:table-cell">
        <button
          @click="deletePosition(p.id)"
          class="text-red-600 hover:text-red-800"
          title="Delete position"
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
  @click="openEditModal(p)"
  class="block w-full text-left px-3 py-2 hover:bg-gray-100"
>
  ✏️ Edit
</button>

            <button
              @click="deletePosition(p.id)"
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
    <h2 class="text-xl font-semibold mb-4">Edit Position</h2>

    <input
      v-model="editPosition.name"
      class="w-full border p-2 mb-4"
      placeholder="Position Name"
    />

    <div class="flex justify-end gap-2">
      <button
        @click="showEditModal = false"
        class="px-4 py-2 bg-gray-300 rounded"
      >
        Cancel
      </button>
      <button
        @click="updatePosition"
        class="px-4 py-2 bg-green-700 text-white rounded"
      >
        Save
      </button>
    </div>
  </div>
</div>

  </div>
</template>
