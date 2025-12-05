// import '@/style.css';
// import 'primeicons/primeicons.css';
// import Toast, { POSITION } from 'vue-toastification';
// import 'vue-toastification/dist/index.css';
// import { createPinia } from 'pinia';
// import router from './router';

// import { createApp } from 'vue';
// import App from './App.vue';

// import "vue-toastification/dist/index.css";


// const app=createApp(App);

// app.use(router);
// app.use(Toast,options);
// app.use(createPinia())

// app.mount('#app');


// const options = {
//   position: POSITION.TOP_RIGHT,
//   timeout: 2500,
//   closeOnClick: true,
//   pauseOnHover: true,
//   draggable: true,
//   draggablePercent: 0.6,
// };

// createApp(App)
//   .use(router)
//   .use(Toast, options)
//   .mount("#app");

import '@/style.css';
import 'primeicons/primeicons.css';

import { createApp } from 'vue';
import App from './App.vue';

import router from './router';
import { createPinia } from 'pinia';

import Toast, { POSITION } from 'vue-toastification';
import 'vue-toastification/dist/index.css';

const options = {
  position: POSITION.TOP_RIGHT,
  timeout: 2500,
  closeOnClick: true,
  pauseOnHover: true,
  draggable: true,
  draggablePercent: 0.6,
};

const app = createApp(App);

app.use(router);
app.use(createPinia());
app.use(Toast, options);

app.mount('#app');
