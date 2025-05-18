<template>
  <div class="app-container">
    <!-- Header với thanh điều hướng -->
    <header class="app-header">
      <div class="header-content">
        <div class="logo">
          <router-link to="/">
            <span class="logo-icon">🛡️🔥</span>
            <span class="logo-text">Fire & Intrusion Warning</span>
          </router-link>
        </div>
        
        <nav class="main-nav">
          <router-link to="/" class="nav-link">Trang chủ</router-link>
          <router-link to="/dashboard" class="nav-link">Dashboard</router-link>
          <router-link v-if="isAdmin" to="/admin" class="nav-link">Quản trị hệ thống</router-link>
        </nav>
        
        <div class="auth-section">
          <template v-if="isLoggedIn">
            <div class="user-menu" @click="toggleUserDropdown">
              <div class="user-avatar">{{ userInitials }}</div>
              <span class="user-name">{{ userName }}</span>
              <span class="dropdown-icon">▼</span>
              
              <div class="dropdown-menu" v-if="showDropdown">
                <router-link to="/profile" class="dropdown-item">Hồ sơ</router-link>
                <router-link to="/dashboard" class="dropdown-item">Dashboard</router-link>
                <router-link v-if="isAdmin" to="/admin" class="dropdown-item">Quản trị hệ thống</router-link>
                <a href="#" @click.prevent="logout" class="dropdown-item">Đăng xuất</a>
              </div>
            </div>
          </template>
          <template v-else>
            <router-link to="/login" class="auth-btn login-btn">Đăng nhập</router-link>
            <router-link to="/register" class="auth-btn register-btn">Đăng ký</router-link>
          </template>
        </div>
      </div>
    </header>
    
    <!-- Nội dung chính -->
    <main class="app-content">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
    
    <!-- Footer -->
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { auth, db } from './firebase';
import { onAuthStateChanged, signOut } from 'firebase/auth';
import { doc, getDoc } from 'firebase/firestore';

export default {
  setup() {
    const isLoggedIn = ref(false);
    const isAdmin = ref(false);
    const userName = ref('Người dùng');
    const userInitials = ref('?');
    const showDropdown = ref(false);
    const router = useRouter();
    
    const toggleUserDropdown = () => {
      showDropdown.value = !showDropdown.value;
    };
    
    const closeDropdownOnClickOutside = (event) => {
      if (showDropdown.value && !event.target.closest('.user-menu')) {
        showDropdown.value = false;
      }
    };
    
    const getUserData = async (user) => {
      try {
        const userDoc = await getDoc(doc(db, "users", user.uid));
        if (userDoc.exists()) {
          const userData = userDoc.data();
          userName.value = userData.name || 'Người dùng';
          
          // Kiểm tra vai trò admin
          isAdmin.value = userData.role === 'admin';
          
          // Lấy chữ cái đầu của tên để hiển thị avatar
          if (userData.name) {
            userInitials.value = userData.name
              .split(' ')
              .map(name => name.charAt(0))
              .join('')
              .toUpperCase()
              .slice(0, 2);
          } else {
            userInitials.value = user.email.charAt(0).toUpperCase();
          }
        }
      } catch (error) {
        console.error("Lỗi khi lấy dữ liệu người dùng:", error);
      }
    };
    
    const logout = async () => {
      try {
        await signOut(auth);
        router.push('/login');
      } catch (error) {
        console.error("Lỗi khi đăng xuất:", error);
      }
    };
    
    onMounted(() => {
      document.addEventListener('click', closeDropdownOnClickOutside);
      
      onAuthStateChanged(auth, (user) => {
        isLoggedIn.value = !!user;
        if (user) {
          getUserData(user);
        } else {
          isAdmin.value = false; // Reset vai trò admin khi đăng xuất
        }
      });
    });
    
    return {
      isLoggedIn,
      isAdmin,
      userName,
      userInitials,
      showDropdown,
      toggleUserDropdown,
      logout
    };
  }
};
</script>

<style>
/* Reset CSS */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  line-height: 1.6;
  color: #333;
  background-color: #f8f9fa;
  min-height: 100vh;
}

a {
  color: inherit;
  text-decoration: none;
}

/* Layout chính */
.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

/* Header Styles */
.app-header {
  background-color: #fff;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.header-content {
  max-width: 1300px;
  margin: 0 auto;
  padding: 15px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo a {
  display: flex;
  align-items: center;
  font-weight: bold;
  color: #007bff;
  font-size: 1.4rem;
}

.logo-icon {
  margin-right: 10px;
}

.main-nav {
  display: flex;
  gap: 25px;
}

.nav-link {
  color: #555;
  font-weight: 500;
  padding: 8px 10px;
  border-radius: 5px;
  transition: all 0.3s ease;
}

.nav-link:hover {
  background-color: #f5f5f5;
  color: #007bff;
}

.router-link-active {
  color: #007bff;
  font-weight: 600;
}

/* Auth Section */
.auth-section {
  display: flex;
  align-items: center;
  gap: 10px;
}

.auth-btn {
  padding: 8px 16px;
  border-radius: 5px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.login-btn {
  color: #007bff;
  border: 1px solid #007bff;
}

.login-btn:hover {
  background-color: #f0f8ff;
}

.register-btn {
  background-color: #007bff;
  color: white;
}

.register-btn:hover {
  background-color: #0056b3;
}

/* User Menu */
.user-menu {
  position: relative;
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 5px 10px;
  border-radius: 5px;
  transition: background-color 0.3s ease;
}

.user-menu:hover {
  background-color: #f5f5f5;
}

.user-avatar {
  width: 35px;
  height: 35px;
  background-color: #007bff;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}

.user-name {
  margin: 0 10px;
  max-width: 120px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.dropdown-icon {
  font-size: 10px;
  color: #777;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  background-color: white;
  width: 200px;
  border-radius: 5px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  padding: 10px 0;
  margin-top: 5px;
  z-index: 100;
}

.dropdown-item {
  display: block;
  padding: 10px 15px;
  transition: background-color 0.3s ease;
}

.dropdown-item:hover {
  background-color: #f5f5f5;
  color: #007bff;
}

/* Main Content */
.app-content {
  flex: 1;
  max-width: 1300px;
  width: 100%;
  margin: 0 auto;
  padding: 20px;
}

/* Animation transition */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

/* Responsive */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 15px;
  }
  
  .main-nav {
    width: 100%;
    justify-content: center;
  }
  
  .auth-section {
    width: 100%;
    justify-content: center;
  }
}
</style>