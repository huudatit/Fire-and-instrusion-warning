<template>
  <div class="auth-container">
    <h2>Đăng ký tài khoản</h2>
    <form @submit.prevent="register" class="auth-form">
      <div class="form-group">
        <label for="name">Họ và tên:</label>
        <input 
          type="text" 
          id="name" 
          v-model="name" 
          required 
          placeholder="Nhập họ và tên của bạn"
        />
      </div>
      
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
          placeholder="Nhập mật khẩu (ít nhất 6 ký tự)"
          minlength="6"
        />
      </div>
      
      <div class="form-group">
        <label for="confirmPassword">Xác nhận mật khẩu:</label>
        <input 
          type="password" 
          id="confirmPassword" 
          v-model="confirmPassword" 
          required 
          placeholder="Nhập lại mật khẩu"
        />
        <p class="error-message" v-if="passwordMismatch">Mật khẩu không khớp</p>
      </div>
      
      <button type="submit" class="submit-btn" :disabled="loading || passwordMismatch">
        {{ loading ? 'Đang xử lý...' : 'Đăng ký' }}
      </button>
      
      <p class="error-message" v-if="errorMessage">{{ errorMessage }}</p>
      
      <div class="auth-links">
        <p>Đã có tài khoản? <router-link to="/login">Đăng nhập</router-link></p>
      </div>
    </form>
  </div>
</template>

<script>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { auth, db } from '../firebase';
import { createUserWithEmailAndPassword } from 'firebase/auth';
import { doc, setDoc } from 'firebase/firestore';

export default {
  setup() {
    const name = ref('');
    const email = ref('');
    const password = ref('');
    const confirmPassword = ref('');
    const errorMessage = ref('');
    const loading = ref(false);
    const router = useRouter();

    const passwordMismatch = computed(() => {
      return password.value && confirmPassword.value && password.value !== confirmPassword.value;
    });

    const register = async () => {
      if (passwordMismatch.value) {
        return;
      }
      
      loading.value = true;
      errorMessage.value = '';
      
      try {
        // Tạo tài khoản người dùng trong Firebase Auth
        const userCredential = await createUserWithEmailAndPassword(
          auth, 
          email.value, 
          password.value
        );
        
        // Lưu thông tin người dùng bổ sung vào Firestore
        await setDoc(doc(db, "users", userCredential.user.uid), {
          name: name.value,
          email: email.value,
          createdAt: new Date(),
          role: 'user'
        });
        
        // Chuyển hướng đến trang chính
        router.push('/');
      } catch (error) {
        console.error('Lỗi đăng ký:', error);
        switch (error.code) {
          case 'auth/email-already-in-use':
            errorMessage.value = 'Email này đã được sử dụng.';
            break;
          case 'auth/invalid-email':
            errorMessage.value = 'Email không hợp lệ.';
            break;
          case 'auth/weak-password':
            errorMessage.value = 'Mật khẩu quá yếu. Vui lòng chọn mật khẩu mạnh hơn.';
            break;
          default:
            errorMessage.value = 'Đăng ký thất bại. Vui lòng thử lại.';
        }
      } finally {
        loading.value = false;
      }
    };

    return {
      name,
      email,
      password,
      confirmPassword,
      passwordMismatch,
      register,
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
  font-size: 14px;
  margin: 0;
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