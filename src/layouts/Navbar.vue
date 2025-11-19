<template>
  <header class="flex items-center justify-between px-6 py-4 bg-white shadow-sm">
    <div class="flex items-center gap-4">
      <div class="text-lg font-semibold text-dns_dark">
        DAVAO DEL NORTE STATE COLLEGE
      </div>
    </div>

    <!-- RIGHT SIDE PROFILE MENU -->
    <div class="relative" ref="containerRef">
      <button
        @click="toggleMenu"
        class="flex items-center gap-2 cursor-pointer select-none"
        aria-haspopup="true"
        :aria-expanded="showMenu.toString()"
      >
        <i class="pi pi-user text-dns_dark text-lg"></i>
        <span class="text-sm text-dns_dark font-medium">Admin</span>

        <svg
          class="w-4 h-4 text-dns_dark"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      <!-- DROPDOWN MENU -->
      <transition name="fade">
        <div
          v-if="showMenu"
          ref="menuRef"
          class="absolute right-0 mt-2 w-48 bg-white shadow-xl rounded-lg border z-50"
        >
          <router-link
            to="/profile"
            class="block px-4 py-2 hover:bg-gray-100 text-sm text-gray-700"
            @click="closeMenu"
          >
            Profile
          </router-link>

          <router-link
            to="/change-password"
            class="block px-4 py-2 hover:bg-gray-100 text-sm text-gray-700"
            @click="closeMenu"
          >
            Change Password
          </router-link>

          <button
            @click="handleLogout"
            class="w-full text-left px-4 py-2 hover:bg-gray-100 text-sm text-gray-700"
          >
            Logout
          </button>
        </div>
      </transition>
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from "vue";
import { useRouter, useRoute } from "vue-router";

const router = useRouter();
const route = useRoute();

const showMenu = ref(false);
const containerRef = ref(null);
const menuRef = ref(null);

function toggleMenu() {
  showMenu.value = !showMenu.value;
}

function closeMenu() {
  showMenu.value = false;
}

function handleLogout() {
  localStorage.removeItem("token");
  closeMenu();
  router.push("/login");
}

// Close when clicking outside
function onDocumentClick(e) {
  const container = containerRef.value;
  if (!container) return;
  if (!container.contains(e.target)) {
    closeMenu();
  }
}

// close on ESC
function onKeyDown(e) {
  if (e.key === "Escape") closeMenu();
}

onMounted(() => {
  document.addEventListener("click", onDocumentClick);
  document.addEventListener("keydown", onKeyDown);
});

// cleanup
onBeforeUnmount(() => {
  document.removeEventListener("click", onDocumentClick);
  document.removeEventListener("keydown", onKeyDown);
});

// close dropdown when navigating to another route
watch(
  () => route.fullPath,
  () => {
    closeMenu();
  }
);
</script>

<style scoped>
/* small fade transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.12s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
