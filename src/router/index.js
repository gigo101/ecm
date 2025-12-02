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
import UploadDocument from '@/views/Documents/UploadDocument.vue'
import DocumentList from '@/views/Documents/DocumentList.vue'
import ChangePassword from '@/views/Auth/ChangePassword.vue'
import Profile from '@/views/Profile.vue'
import Userlist from '@/views/Userlist.vue'

const routes = [
{ 
    path: '/', 
    component: Login
},
{ 
    path: '/dashboard', 
    component: Dashboard
},
{ 
    path: '/documentss', 
    component: Documents 
},
{ 
    path: '/upload2', 
    component: Upload 
},
{
  path: "/documents/upload",
  component: UploadDocument
},
{
  path: "/documents",
  name: "Documents",
  component: DocumentList
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
  path: "/change-password",
  component: ChangePassword
},
{
  path: "/profile",
  component: Profile,
  meta: { requiresAuth: true }
},
{
  path: "/users",
  component: Userlist,
  meta: { requiresAuth: true, requiresAdmin: true }
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


router.beforeEach((to, from, next) => {
  const token = localStorage.getItem("token");

  // Protected pages
  const protectedPages = ["/dashboard", "/documents", "/documents/upload", "/change-pasword"];

  if (protectedPages.includes(to.path) && !token) {
    next("/login"); // Redirect if not logged in
  } else {
    next();
  }

  if (to.meta.requiresAdmin && localStorage.getItem("role") !== "Admin") {
  return next("/unauthorized");
}

});
