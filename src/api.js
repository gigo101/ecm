// import axios from "axios";

// const api = axios.create({
//   baseURL: "http://localhost:8000", // your FastAPI URL
// });

// api.interceptors.request.use((config) => {
//   const token = localStorage.getItem("token");
//   if (token) {
//     config.headers.Authorization = `Bearer ${token}`;
//   }
//   return config;
// });

// export default api;

// src/api.js
// import axios from "axios";

// const api = axios.create({
//   baseURL: "http://127.0.0.1:8000", // your FastAPI backend URL
// });

// export default api;

import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

// Auto-attach JWT
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export default api;
