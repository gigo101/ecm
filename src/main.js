import '@/style.css';
import 'primeicons/primeicons.css';
import Toast from 'vue-toastification';
import 'vue-toastification/dist/index.css';
import { createPinia } from 'pinia';
import router from './router';

import { createApp } from 'vue';
import App from './App.vue';

const app=createApp(App);

app.use(router);
app.use(Toast);
app.use(createPinia())

app.mount('#app');









