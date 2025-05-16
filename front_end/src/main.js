import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import "./assets/main.css"; // Import file CSS chính

// Tạo ứng dụng Vue và gắn vào DOM
createApp(App).use(router).mount("#app");
