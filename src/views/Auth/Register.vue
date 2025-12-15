<script setup>
import { ref, onMounted } from "vue";
import api from "../../api";
import { useRouter } from "vue-router";

const router = useRouter();

// STEP CONTROL
const step = ref(1);

// FORM FIELDS
const first_name = ref("");
const middle_name = ref("");
const last_name = ref("");
const suffix = ref("");

const position = ref("");
const office = ref("");

const email = ref("");
const password = ref("");
const confirmPassword = ref("");

// DROPDOWN DATA
const positions = ref([]);
const offices = ref([]);

// UI STATE
const loading = ref(false);
const error = ref("");
const success = ref("");

// LOAD POSITIONS & OFFICES FROM API
onMounted(async () => {
  try {
    const [posRes, offRes] = await Promise.all([
      api.get("/positions"),
      api.get("/offices"),
    ]);

    positions.value = posRes.data;
    offices.value = offRes.data;
  } catch (err) {
    console.error("Failed to load positions/offices", err);
    error.value = "Failed to load form data. Please refresh.";
  }
});

// STEP NAVIGATION
function nextStep() {
  error.value = "";

  if (step.value === 1 && (!first_name.value || !last_name.value)) {
    error.value = "Please enter all required personal details.";
    return;
  }

  if (step.value === 2 && (!position.value || !office.value)) {
    error.value = "Please provide your position and office.";
    return;
  }

  step.value++;
}

function previousStep() {
  error.value = "";
  step.value--;
}

// REGISTER
async function handleRegister() {
  error.value = "";
  success.value = "";

  if (password.value !== confirmPassword.value) {
    error.value = "Passwords do not match.";
    return;
  }

  loading.value = true;

  try {
    await api.post("/auth/register", {
      first_name: first_name.value,
      middle_name: middle_name.value,
      last_name: last_name.value,
      suffix: suffix.value,
      position: position.value,   // ← position code or name
      office: office.value,       // ← office_code
      email: email.value,
      password: password.value,
    });

    success.value = "Account successfully created!";
    setTimeout(() => router.push("/login"), 2000);

  } catch (err) {
    error.value = err.response?.data?.detail || "Registration failed.";
  } finally {
    loading.value = false;
  }
}
</script>



<template>
  <div
    class="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-900 via-green-800 to-green-700 bg-cover bg-center"
    style="background-image: url('/images/bg-building.jpg'); background-blend-mode: overlay;"
  >
    <div class="bg-white/80 backdrop-blur-lg p-10 rounded-3xl shadow-2xl w-full max-w-md">

      <!-- STEP INDICATOR -->
      <div class="flex justify-center mb-6">
        <div class="flex gap-3">
          <div :class="['w-3 h-3 rounded-full', step === 1 ? 'bg-green-700' : 'bg-gray-400']"></div>
          <div :class="['w-3 h-3 rounded-full', step === 2 ? 'bg-green-700' : 'bg-gray-400']"></div>
          <div :class="['w-3 h-3 rounded-full', step === 3 ? 'bg-green-700' : 'bg-gray-400']"></div>
        </div>
      </div>

      <h2 class="text-3xl font-extrabold text-green-800 text-center mb-6">
        Create Account
      </h2>

      <form @submit.prevent="handleRegister" class="space-y-4">

        <!-- STEP 1: PERSONAL INFO -->
        <div v-if="step === 1" class="space-y-4">
          <h3 class="text-lg font-semibold text-green-700">Personal Information</h3>

          <div>
            <label class="block text-gray-700 mb-1 text-sm">First Name</label>
            <input v-model="first_name" required class="w-full p-3 border rounded-lg" />
          </div>

          <div>
            <label class="block text-gray-700 mb-1 text-sm">Middle Name</label>
            <input v-model="middle_name" class="w-full p-3 border rounded-lg" />
          </div>

          <div>
            <label class="block text-gray-700 mb-1 text-sm">Last Name</label>
            <input v-model="last_name" required class="w-full p-3 border rounded-lg" />
          </div>

          <div>
            <label class="block text-gray-700 mb-1 text-sm">Suffix (optional)</label>
            <input v-model="suffix" class="w-full p-3 border rounded-lg" />
          </div>

          <button type="button" @click="nextStep" class="w-full bg-green-700 hover:bg-green-800 text-white p-3 rounded-lg">
            Next →
          </button>
        </div>

        <!-- STEP 2: WORK INFO -->
        <!-- STEP 2: WORK INFO -->
        <div v-if="step === 2" class="space-y-4">
          <h3 class="text-lg font-semibold text-green-700">Work Information</h3>

          <!-- Position Dropdown -->
          <div>
            <label class="block text-gray-700 mb-1 text-sm">Position</label>
<select
  v-model="position"
  required
  class="w-full p-3 border rounded-lg"
>
  <option disabled value="">Select Position</option>

  <option
    v-for="p in positions"
    :key="p.id"
    :value="p.name"
  >
    {{ p.name }}
  </option>
</select>

          </div>

          <!-- Office Dropdown -->
          <div>
            <label class="block text-gray-700 mb-1 text-sm">Office</label>
<select
  v-model="office"
  required
  class="w-full p-3 border rounded-lg"
>
  <option disabled value="">Select Office</option>

  <option
    v-for="o in offices"
    :key="o.id"
    :value="o.office_code"
  >
    {{ o.name }} ({{ o.office_code }})
  </option>
</select>

          </div>

  <div class="flex justify-between">
    <button
      type="button"
      @click="previousStep"
      class="px-5 py-2 bg-gray-400 rounded text-white"
    >
      ← Back
    </button>

    <button
      type="button"
      @click="nextStep"
      class="px-5 py-2 bg-green-700 text-white rounded"
    >
      Next →
    </button>
  </div>
</div>


        <!-- STEP 3: ACCOUNT INFO -->
        <div v-if="step === 3" class="space-y-4">
          <h3 class="text-lg font-semibold text-green-700">Account Credentials</h3>

          <div>
            <label class="block text-gray-700 mb-1 text-sm">Email</label>
            <input type="email" v-model="email" required class="w-full p-3 border rounded-lg" />
          </div>

          <div>
            <label class="block text-gray-700 mb-1 text-sm">Password</label>
            <input type="password" v-model="password" required class="w-full p-3 border rounded-lg" />
          </div>

          <div>
            <label class="block text-gray-700 mb-1 text-sm">Confirm Password</label>
            <input type="password" v-model="confirmPassword" required class="w-full p-3 border rounded-lg" />
          </div>

          <div class="flex justify-between">
            <button type="button" @click="previousStep" class="px-5 py-2 bg-gray-400 rounded text-white">
              ← Back
            </button>

            <button type="submit" :disabled="loading" class="px-5 py-2 bg-green-700 hover:bg-green-800 text-white rounded">
              <span v-if="!loading">Register</span>
              <span v-else>Creating...</span>
            </button>
          </div>
        </div>

        <!-- Error / Success -->
        <div v-if="error" class="text-red-600 text-center text-sm">{{ error }}</div>
        <div v-if="success" class="text-green-700 text-center text-sm font-semibold">{{ success }}</div>

      </form>

      <p class="text-center text-sm text-gray-600 mt-6">
        Already have an account?
        <router-link to="/login" class="text-green-700 hover:underline">Log in</router-link>
      </p>

    </div>
  </div>
</template>
