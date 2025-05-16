<template>
  <div class="auth-container">
    <h2>Quên mật khẩu</h2>
    <div v-if="resetSent" class="success-message">
      <p>Đã gửi email khôi phục mật khẩu!</p>
      <p>Vui lòng kiểm tra hộp thư đến của bạn và làm theo hướng dẫn để đặt lại mật khẩu.</p>
      <router-link to="/login" class="btn btn-primary">Quay lại đăng nhập</router-link>
    </div>
    
    <form v-else @submit.prevent="resetPassword" class="auth-form">
      <div class="form-group">
        <label for="email">Email của bạn:</label>
        <input 
          type="email" 
          id="email" 
          v-model="email" 
          required 
          placeholder="Nhập email đã đăng ký"
        />
      </div>
      
      <button type="submit" class="submit-btn" :disabled="loading">
        {{ loading ? 'Đang xử lý...' : 'Gửi yêu cầu đặt lại mật khẩu' }}
      </button>
      
      <p class="error-message" v-if="errorMessage">{{ errorMessage }}</p>
      
      <div class="auth-links">
        <p><router-link to="/login">Quay lại đăng nhập</router-link></p>
      </div>
    </form>
  </div>
</template>

<script>
import { ref } from 'vue';
import { auth } from '../firebase';
import { sendPasswordResetEmail } from 'firebase/auth';

export default {
  setup() {
    const email = ref('');
    const errorMessage = ref('');
    const loading = ref(false);
    const resetSent = ref(false);

    const resetPassword = async () => {
      loading.value = true;
      errorMessage.value = '';
      
      try {
        await sendPasswordResetEmail(auth, email.value);
        resetSent.value = true;
      } catch (error) {
        console.error('Lỗi gửi email đặt lại mật khẩu:', error);
        switch (error.code) {
          case 'auth/invalid-email':
            errorMessage.value = 'Email không hợp lệ.';
            break;
          case 'auth/user-not-found':
            errorMessage.value = 'Không tìm thấy tài khoản với email này.';
            break;
          default:
            errorMessage.value = 'Không thể gửi email đặt lại mật khẩu. Vui lòng thử lại sau.';
        }
      } finally {
        loading.value = false;
      }
    };

    return {
      email,
      errorMessage,
      loading,
      resetSent,
      resetPassword
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

.success-message {
  text-align: center;
  color: #28a745;
  line-height: 1.6;
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

.btn {
  display: inline-block;
  padding: 10px 20px;
  margin-top: 15px;
  border-radius: 5px;
  font-weight: 500;
  text-decoration: none;
  transition: background-color 0.3s ease;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-primary:hover {
  background-color: #0056b3;
}
</style>