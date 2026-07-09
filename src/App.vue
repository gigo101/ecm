<template>

    <AppLayout v-if="route.meta.layout === 'app'">
        <router-view />
    </AppLayout>

    <AuthLayout v-else>
        <router-view />
    </AuthLayout>

</template>

<script setup>
import { useRoute } from "vue-router"

import AppLayout from "@/layouts/AppLayout.vue"
import AuthLayout from "@/layouts/AuthLayout.vue"

const route = useRoute()
</script>