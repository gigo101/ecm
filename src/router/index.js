import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '@/views/Dashboard.vue'
import Documents from '@/views/Documents/List.vue'
import Upload from '@/views/Documents/Upload.vue'
import Search from '@/views/Search/SmartSearch.vue'
import Chatbot from '@/views/Chatbot.vue'
import Login from '@/views/Auth/Login.vue'
import AdminUsers from '@/views/Admin/Users.vue'
import NotFoundView from "@/views/NotFound.vue";
import Login2 from '@/views/Login2.vue'; 
import AddNumber from '@/views/AddNumbers.vue';
import Register from '@/views/Auth/Register.vue'

const routes = [
{ 
    path: '/', 
    component: Dashboard 
},
{ 
    path: '/documents', 
    component: Documents 
},
{ 
    path: '/upload', 
    component: Upload 
},
{ 
    path: '/search', 
    component: Search 
},
{ 
    path: '/chat', 
    component: Chatbot 
},
{ 
    path: '/login', 
    component: Login 
},
{ 
    path: '/login2', 
    component: Login2
},
{ 
    path: '/register', 
    component: Register
},
{ 
    path: '/admin/users', 
    component: AdminUsers 
},
{ 
    path: '/addnumber', 
    component: AddNumber 
},
{ 
    path: '/:catchAll(.*)', 
    name: 'not-found',
    component: NotFoundView
}

]

const router = createRouter({
history: createWebHistory(),
routes
})

export default router
