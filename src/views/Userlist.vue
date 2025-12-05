<template>
  <div class="p-8">
    <h1 class="text-2xl font-semibold text-dns_dark mb-6">
      User Management
    </h1>

    <div v-if="loading">Loading users...</div>
    <div v-if="error" class="text-red-600">{{ error }}</div>

<table class="w-full bg-white rounded shadow">
  <thead class="bg-green-700 text-white">
    <tr>
      <th class="p-3 text-left">First Name</th>
      <th class="p-3 text-left">Middle Name</th>
      <th class="p-3 text-left">Last Name</th>
      <th class="p-3 text-left">Email</th>
      <th class="p-3 text-left">Role</th>
      <th class="p-3 text-left">Created</th>

      <!-- Desktop action columns -->
      <th class="p-3 text-center hidden md:table-cell">Edit</th>
      <th class="p-3 text-center hidden md:table-cell">Password</th>
      <th class="p-3 text-center hidden md:table-cell">Role</th>
      <th class="p-3 text-center hidden md:table-cell">Delete</th>
      <th class="p-3 text-left">Status</th>


      <!-- Mobile dropdown -->
      <th class="p-3 text-center md:hidden">Actions</th>
    </tr>
  </thead>

  <tbody>
    <tr v-for="u in users" :key="u.id" class="border-b">
      <td class="p-3">{{ u.first_name }}</td>
      <td class="p-3">{{ u.middle_name }}</td>
      <td class="p-3">{{ u.last_name }}</td>
      <td class="p-3">{{ u.email }}</td>
      <td class="p-3">{{ u.role }}</td>
      <td class="p-3">{{ u.created_at }}</td>

      <!-- Desktop icon buttons with tooltips -->
      <td class="p-3 text-center hidden md:table-cell">
        <button
          @click="openEditModal(u)"
          class="text-blue-600 hover:text-blue-800"
          title="Edit user"
        >
          ✏️
        </button>
      </td>

      <td class="p-3 text-center hidden md:table-cell">
        <button
          @click="openPasswordModal(u)"
          class="text-yellow-600 hover:text-yellow-800"
          title="Change password"
        >
          🔑
        </button>
      </td>

      <td class="p-3 text-center hidden md:table-cell">
        <button
          @click="openRoleModal(u)"
          class="text-green-700 hover:text-green-900"
          title="Edit role"
        >
          🛠️
        </button>
      </td>

      <td class="p-3 text-center hidden md:table-cell">
        <button
          @click="deleteUser(u.id)"
          class="text-red-600 hover:text-red-800"
          title="Delete user"
        >
          🗑️
        </button>
      </td>

      <td class="p-3">

  <!-- Toggle Switch -->
  <label class="inline-flex items-center cursor-pointer">
    <input
      type="checkbox"
      class="sr-only peer"
      :checked="u.is_active"
      @change="toggleStatus(u)"
    />
    <div
      class="w-11 h-6 bg-gray-300 rounded-full peer peer-checked:bg-green-600 relative transition"
    >
      <div
        class="absolute left-1 top-1 w-4 h-4 bg-white rounded-full transition
               peer-checked:translate-x-5"
      ></div>
    </div>
  </label>

</td>

      <!-- Mobile dropdown -->
      <td class="p-3 md:hidden text-center">
        <details class="relative inline-block">
          <summary class="cursor-pointer py-1 px-3 bg-gray-200 rounded">
            ⋮
          </summary>

          <div class="absolute right-0 mt-1 bg-white border shadow rounded w-32 z-20">
            <button @click="openEditModal(u)" class="block w-full text-left px-3 py-2 hover:bg-gray-100">✏️ Edit</button>
            <button @click="openPasswordModal(u)" class="block w-full text-left px-3 py-2 hover:bg-gray-100">🔑 Password</button>
            <button @click="openRoleModal(u)" class="block w-full text-left px-3 py-2 hover:bg-gray-100">🛠️ Edit Role</button>
            <button @click="deleteUser(u.id)" class="block w-full text-left px-3 py-2 hover:bg-red-100 text-red-600">🗑️ Delete</button>
          </div>
        </details>
      </td>

    </tr>
  </tbody>
</table>


    <!-- ROLE MODAL -->
    <div v-if="showRoleModal" class="fixed inset-0 bg-black/40 flex items-center justify-center">
      <div class="bg-white p-6 rounded-lg w-96 shadow-lg">
        <h2 class="text-xl font-semibold mb-4">Update Role</h2>

        <select v-model="newRole" class="w-full p-3 border rounded mb-4">
          <option v-for="r in roles" :key="r" :value="r">{{ r }}</option>
        </select>

        <div class="flex justify-end gap-2">
          <button @click="showRoleModal = false" class="px-4 py-2 bg-gray-300 rounded">
            Cancel
          </button>
          <button @click="updateRole" class="px-4 py-2 bg-green-700 text-white rounded">
            Save
          </button>
        </div>
      </div>
    </div>

    <!-- EDIT USER MODAL -->
    <div v-if="showEditModal" class="fixed inset-0 bg-black/40 flex items-center justify-center">
      <div class="bg-white p-6 rounded-lg w-96 shadow-lg">
        <h2 class="text-xl font-semibold mb-4">Edit User</h2>

        <input v-model="editUser.first_name" class="w-full border p-2 mb-3" placeholder="First Name" />
        <input v-model="editUser.middle_name" class="w-full border p-2 mb-3" placeholder="Middle Name" />
        <input v-model="editUser.last_name" class="w-full border p-2 mb-3" placeholder="Last Name" />
        <input v-model="editUser.email" class="w-full border p-2 mb-3" placeholder="Email" />

        <div class="flex justify-end gap-2">
          <button @click="showEditModal = false" class="px-4 py-2 bg-gray-300 rounded">Cancel</button>
          <button @click="saveUserChanges" class="px-4 py-2 bg-green-700 text-white rounded">Save</button>
        </div>
      </div>
    </div>

    <!-- PASSWORD MODAL -->
    <div v-if="showPasswordModal" class="fixed inset-0 bg-black/40 flex items-center justify-center">
      <div class="bg-white p-6 rounded-lg w-96 shadow-lg">
        <h2 class="text-xl font-semibold mb-4">Change Password</h2>

        <input type="password" v-model="passwordForm.old_password" class="w-full border p-2 mb-3"
          placeholder="Old Password" />

        <input type="password" v-model="passwordForm.new_password" class="w-full border p-2 mb-3"
          placeholder="New Password" />

        <div class="flex justify-end gap-2">
          <button @click="showPasswordModal = false" class="px-4 py-2 bg-gray-300 rounded">Cancel</button>
          <button @click="savePasswordChange" class="px-4 py-2 bg-green-700 text-white rounded">Save</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "@/api";

const users = ref([]);
const loading = ref(true);
const error = ref("");

const roles = ["Admin", "Uploader", "Faculty", "Staff", "Viewer"];

const showRoleModal = ref(false);
const selectedUser = ref(null);
const newRole = ref("");

const showEditModal = ref(false);
const showPasswordModal = ref(false);

const editUser = ref({
  id: null,
  first_name: "",
  middle_name: "",
  last_name: "",
  email: "",
  role: "",
});

const passwordForm = ref({
  id: null,
  old_password: "",
  new_password: "",
});

async function loadUsers() {
  loading.value = true;

  try {
    const res = await api.get("/users");
    users.value = res.data;
  } catch (err) {
    error.value = "Failed to load users.";
  } finally {
    loading.value = false;
  }
}

function openRoleModal(user) {
  selectedUser.value = user;
  newRole.value = user.role;
  showRoleModal.value = true;
}

async function updateRole() {
  try {
    await api.put(`/users/${selectedUser.value.id}/role`, null, {
      params: { role: newRole.value },
    });
    showRoleModal.value = false;
    loadUsers();
    alert("User role updated successfully.");
  } catch {
    alert("Failed to update role.");
  }
}

async function deleteUser(id) {
  if (!confirm("Delete this user?")) return;
  await api.delete(`/users/${id}`);
  loadUsers();
}

function openEditModal(user) {
  editUser.value = { ...user };
  showEditModal.value = true;
}

function openPasswordModal(user) {
  passwordForm.value = {
    id: user.id,
    old_password: "",
    new_password: ""
  };
  showPasswordModal.value = true;
}

async function saveUserChanges() {
  await api.put(`/users/${editUser.value.id}`, editUser.value);
  showEditModal.value = false;
  loadUsers();
  alert("User updated successfully.");
}

async function savePasswordChange() {
  await api.put(`/users/${passwordForm.value.id}/password`, {
    old_password: passwordForm.value.old_password,
    new_password: passwordForm.value.new_password,
  });
  showPasswordModal.value = false;
}


 async function toggleStatus(user) {
  try {
    const newStatus = !user.is_active;

    await api.put(`/users/${user.id}/status`, {
      is_active: newStatus
    });

    user.is_active = newStatus; // Update UI optimistically
  } catch (err) {
    alert("Failed to update user status.");
  }
}

onMounted(loadUsers);
</script>
