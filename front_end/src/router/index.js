import { createRouter, createWebHistory } from "vue-router";
import { auth, db } from "../firebase";
import { doc, getDoc } from "firebase/firestore";
import HomeView from "../views/HomeView.vue";

// Middleware kiểm tra xác thực được cải tiến
const requireAuth = (to, from, next) => {
  // Thêm trạng thái loading để tránh nhấp nháy UI
  const unsubscribe = auth.onAuthStateChanged((user) => {
    if (user) {
      next();
    } else {
      next({
        path: "/login",
        query: { redirect: to.fullPath }, // Lưu đường dẫn để redirect sau khi đăng nhập
      });
    }
    unsubscribe();
  });
};

// Middleware ngăn người dùng đã đăng nhập vào các trang đăng nhập/đăng ký
const redirectIfAuth = (to, from, next) => {
  const unsubscribe = auth.onAuthStateChanged((user) => {
    if (user) {
      next("/dashboard");
    } else {
      next();
    }
    unsubscribe();
  });
};

// Middleware kiểm tra quyền admin
const requireAdmin = (to, from, next) => {
  const unsubscribe = auth.onAuthStateChanged(async (user) => {
    if (user) {
      try {
        // Lấy thông tin người dùng từ Firestore
        const userDoc = await getDoc(doc(db, "users", user.uid));
        if (userDoc.exists() && userDoc.data().role === "admin") {
          // Người dùng có quyền admin
          next();
        } else {
          // Người dùng không có quyền admin
          alert("Bạn không có quyền truy cập trang này");
          next("/dashboard");
        }
      } catch (error) {
        console.error("Lỗi khi kiểm tra quyền admin:", error);
        next("/dashboard");
      }
    } else {
      next({
        path: "/login",
        query: { redirect: to.fullPath },
      });
    }
    unsubscribe();
  });
};

const routes = [
  {
    path: "/",
    name: "home",
    component: HomeView,
    meta: {
      title: "Trang chủ - Fire & Intrusion Warning",
    },
  },
  {
    path: "/dashboard",
    name: "dashboard",
    component: () => import("../views/DashboardView.vue"),
    beforeEnter: requireAuth,
    meta: {
      title: "Dashboard - Fire & Intrusion Warning",
    },
  },
  {
    path: "/admin",
    name: "admin",
    component: () => import("../views/AdminDashboard.vue"),
    beforeEnter: requireAdmin,
    meta: {
      title: "Quản trị hệ thống - Fire & Intrusion Warning",
      requiresAdmin: true,
    },
  },

  {
    path: "/login",
    name: "login",
    component: () => import("../views/LoginView.vue"),
    beforeEnter: redirectIfAuth,
    meta: {
      title: "Đăng nhập - Fire & Intrusion Warning",
    },
  },
  {
    path: "/register",
    name: "register",
    component: () => import("../views/RegisterView.vue"),
    beforeEnter: redirectIfAuth,
    meta: {
      title: "Đăng ký - Fire & Intrusion Warning",
    },
  },
  {
    path: "/forgot-password",
    name: "forgot-password",
    component: () => import("../views/ForgotPasswordView.vue"),
    beforeEnter: redirectIfAuth,
    meta: {
      title: "Quên mật khẩu - Fire & Intrusion Warning",
    },
  },
  {
    path: "/profile",
    name: "profile",
    component: () => import("../views/ProfileView.vue"),
    beforeEnter: requireAuth,
    meta: {
      title: "Hồ sơ - Fire & Intrusion Warning",
    },
  },
  // Thêm trang 404 Not Found
  {
    path: "/:pathMatch(.*)*",
    name: "not-found",
    // Sử dụng component trực tiếp thay vì import động
    component: {
      template: `
        <div class="not-found-container">
          <div class="error-code">404</div>
          <h1>Không tìm thấy trang</h1>
          <p>Trang bạn đang tìm kiếm không tồn tại hoặc đã được di chuyển.</p>
          <div class="action-buttons">
            <router-link to="/" class="btn-primary">Về trang chủ</router-link>
            <button @click="goBack" class="btn-secondary">Quay lại</button>
          </div>
        </div>
      `,
      methods: {
        goBack() {
          this.$router.go(-1);
        },
      },
    },
    meta: {
      title: "Không tìm thấy trang - Fire & Intrusion Warning",
    },
  },
];

const router = createRouter({
  // Thay thế import.meta.env.BASE_URL bằng '/' nếu gặp vấn đề
  history: createWebHistory("/"),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      // Nếu có vị trí đã lưu (khi sử dụng nút Back)
      return savedPosition;
    } else {
      // Cuộn lên đầu trang khi chuyển trang
      return { top: 0 };
    }
  },
});

// Middleware toàn cục để cập nhật tiêu đề trang
router.beforeEach((to, from, next) => {
  // Cập nhật title dựa vào meta của route
  document.title = to.meta.title || "Fire & Intrusion Warning System";
  next();
});

export default router;
