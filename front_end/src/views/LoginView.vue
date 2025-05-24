<template>
  <div class="auth-container">
    <h2>Đăng nhập</h2>
    <form @submit.prevent="login" class="auth-form">
      <div class="form-group">
        <label for="email">Email:</label>
        <input 
          type="email" 
          id="email" 
          v-model="email" 
          required 
          placeholder="Nhập email của bạn"
        />
      </div>
      
      <div class="form-group">
        <label for="password">Mật khẩu:</label>
        <input 
          type="password" 
          id="password" 
          v-model="password" 
          required 
          placeholder="Nhập mật khẩu"
        />
      </div>
      
      <button type="submit" class="submit-btn" :disabled="loading">
        {{ loading ? 'Đang xử lý...' : 'Đăng nhập' }}
      </button>
      
      <p class="error-message" v-if="errorMessage">{{ errorMessage }}</p>
      
      <div class="auth-links">
        <p>Chưa có tài khoản? <router-link to="/register">Đăng ký ngay</router-link></p>
        <p><router-link to="/forgot-password">Quên mật khẩu?</router-link></p>
      </div>
    </form>
  </div>
</template>

<script>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { auth } from '../firebase';
import { signInWithEmailAndPassword } from 'firebase/auth';
import { getDoc, doc } from "firebase/firestore";
import { db } from '../firebase'; 

export default {
  setup() {
    const email = ref('');
    const password = ref('');
    const errorMessage = ref('');
    const loading = ref(false);
    const router = useRouter();

   const login = async () => {
    loading.value = true;
    errorMessage.value = '';

    try {
      const userCredential = await signInWithEmailAndPassword(auth, email.value, password.value);
      const user = userCredential.user;

      // Lấy role từ Firestore
      const userDocRef = doc(db, "users", user.uid);
      const userSnapshot = await getDoc(userDocRef);

      if (userSnapshot.exists()) {
        const userData = userSnapshot.data();
        const role = userData.role || "user"; // mặc định là user nếu không có

        localStorage.setItem("userEmail", email.value);
        localStorage.setItem("userRole", role); 

        // Gửi email tới Flask backend
        const response = await fetch('http://localhost:5000/api/set_email', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ email: email.value })
        });

        const result = await response.json();
        console.log("Phản hồi từ server:", result);

        if (response.ok) {
          setTimeout(() => {
            router.push('/dashboard');
          }, 300);
        } else {
          alert("Không thể lưu email người dùng trên server.");
        }
      } else {
        alert("Không tìm thấy thông tin người dùng.");
      }
    } catch (error) {
      console.error('Lỗi đăng nhập:', error);
      errorMessage.value = "Email hoặc mật khẩu không đúng.";
    }
  };

    return {
      email,
      password,
      login,
      errorMessage,
      loading
    };
  }
};
</script>

<style scoped>
.auth-container {
  max-width: 400px;
  margin: 40px auto;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
  background-color: #fff;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.form-group label {
  font-weight: 500;
  text-align: left;
}

.form-group input {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 16px;
}

.submit-btn {
  background-color: #007bff;
  color: white;
  padding: 12px;
  border: none;
  border-radius: 5px;
  font-size: 16px;
  cursor: pointer;
  margin-top: 10px;
}

.submit-btn:hover {
  background-color: #0056b3;
}

.submit-btn:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.error-message {
  color: red;
  text-align: center;
  margin: 10px 0;
}

.auth-links {
  margin-top: 15px;
  text-align: center;
}

.auth-links a {
  color: #007bff;
  text-decoration: none;
}

.auth-links a:hover {
  text-decoration: underline;
}
</style>