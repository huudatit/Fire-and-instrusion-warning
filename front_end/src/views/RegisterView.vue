<template>
  <div class="auth-container">
    <h2>Đăng ký tài khoản</h2>
    
    <div v-if="registrationSuccess" class="success-message">
      <div class="alert alert-success">
        <h4>Đăng ký thành công!</h4>
        <p>Tài khoản của bạn đã được tạo thành công. Bạn sẽ được chuyển hướng đến trang chủ trong giây lát...</p>
      </div>
    </div>
    
    <form v-else @submit.prevent="register" class="auth-form">
      <div class="form-group">
        <label for="name">Họ và tên:</label>
        <input 
          type="text" 
          id="name" 
          v-model="name" 
          required 
          placeholder="Nhập họ và tên của bạn"
          :class="{ 'error-input': formSubmitted && !name }"
        />
        <p class="error-message" v-if="formSubmitted && !name">Vui lòng nhập họ và tên</p>
      </div>
      
      <div class="form-group">
        <label for="email">Email:</label>
        <input 
          type="email" 
          id="email" 
          v-model="email" 
          required 
          placeholder="Nhập email của bạn"
          :class="{ 'error-input': formSubmitted && !isValidEmail }"
        />
        <p class="error-message" v-if="formSubmitted && !isValidEmail">Email không hợp lệ</p>
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
          :class="{ 'error-input': formSubmitted && !isValidPassword }"
        />
        <p class="error-message" v-if="formSubmitted && !isValidPassword">
          Mật khẩu phải có ít nhất 6 ký tự
        </p>
      </div>
      
      <div class="form-group">
        <label for="confirmPassword">Xác nhận mật khẩu:</label>
        <input 
          type="password" 
          id="confirmPassword" 
          v-model="confirmPassword" 
          required 
          placeholder="Nhập lại mật khẩu"
          :class="{ 'error-input': formSubmitted && passwordMismatch }"
        />
        <p class="error-message" v-if="formSubmitted && passwordMismatch">Mật khẩu không khớp</p>
      </div>
      
      <button type="submit" class="submit-btn" :disabled="loading">
        <span v-if="loading" class="spinner"></span>
        {{ loading ? 'Đang xử lý...' : 'Đăng ký' }}
      </button>
      
      <div v-if="errorMessage" class="alert alert-danger mt-3">
        <strong>Lỗi:</strong> {{ errorMessage }}
      </div>
      
      <div class="auth-links">
        <p>Đã có tài khoản? <router-link to="/login">Đăng nhập</router-link></p>
      </div>
    </form>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { auth, db } from '../firebase';
import { createUserWithEmailAndPassword, sendEmailVerification } from 'firebase/auth';
import { doc, setDoc, serverTimestamp } from 'firebase/firestore';

export default {
  setup() {
    const name = ref('');
    const email = ref('');
    const password = ref('');
    const confirmPassword = ref('');
    const errorMessage = ref('');
    const loading = ref(false);
    const formSubmitted = ref(false);
    const registrationSuccess = ref(false);
    const router = useRouter();

    const isValidEmail = computed(() => {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      return !email.value || emailRegex.test(email.value);
    });

    const isValidPassword = computed(() => {
      return !password.value || password.value.length >= 6;
    });

    const passwordMismatch = computed(() => {
      return password.value && confirmPassword.value && password.value !== confirmPassword.value;
    });

    const validateForm = () => {
      formSubmitted.value = true;
      
      if (!name.value || !email.value || !password.value || !confirmPassword.value) {
        return false;
      }
      
      if (!isValidEmail.value) {
        return false;
      }
      
      if (!isValidPassword.value) {
        return false;
      }
      
      if (passwordMismatch.value) {
        return false;
      }
      
      // Đã loại bỏ đoạn kiểm tra acceptTerms.value
      
      return true;
    };

    const register = async () => {
      if (!validateForm()) {
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
        
        console.log("Tài khoản đã được tạo:", userCredential.user.uid);
        
        // Gửi email xác thực (tuỳ chọn)
        try {
          await sendEmailVerification(userCredential.user);
          console.log("Email xác thực đã được gửi");
        } catch (verifyError) {
          console.warn("Không thể gửi email xác thực:", verifyError);
          // Tiếp tục quá trình đăng ký ngay cả khi không gửi được email xác thực
        }
        
        // Lưu thông tin người dùng bổ sung vào Firestore
        await setDoc(doc(db, "users", userCredential.user.uid), {
          name: name.value,
          email: email.value,
          createdAt: serverTimestamp(),
          role: 'user',
          verified: false,
          lastLogin: serverTimestamp()
        });
        
        console.log("Dữ liệu người dùng đã được lưu vào Firestore");
        
        // Hiển thị thông báo thành công
        registrationSuccess.value = true;
        
        // Chuyển hướng đến trang Home sau 2 giây
        setTimeout(() => {
          router.push('/');
          console.log("Chuyển hướng về trang Home");
        }, 2000);
        
      } catch (error) {
        console.error('Lỗi đăng ký:', error);
        switch (error.code) {
          case 'auth/email-already-in-use':
            errorMessage.value = 'Email này đã được sử dụng bởi tài khoản khác.';
            break;
          case 'auth/invalid-email':
            errorMessage.value = 'Email không hợp lệ.';
            break;
          case 'auth/weak-password':
            errorMessage.value = 'Mật khẩu quá yếu. Vui lòng chọn mật khẩu mạnh hơn.';
            break;
          case 'auth/network-request-failed':
            errorMessage.value = 'Lỗi kết nối mạng. Vui lòng kiểm tra kết nối internet của bạn.';
            break;
          case 'auth/too-many-requests':
            errorMessage.value = 'Quá nhiều yêu cầu không thành công. Vui lòng thử lại sau.';
            break;
          default:
            errorMessage.value = `Đăng ký thất bại: ${error.message}`;
        }
      } finally {
        loading.value = false;
      }
    };

    onMounted(() => {
      // Reset form khi component được mount
      formSubmitted.value = false;
      errorMessage.value = '';
    });

    return {
      name,
      email,
      password,
      confirmPassword,
      passwordMismatch,
      errorMessage,
      loading,
      formSubmitted,
      registrationSuccess,
      isValidEmail,
      isValidPassword,
      register
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

.error-input {
  border-color: #dc3545 !important;
  background-color: #fff8f8;
}

.form-check {
  display: flex;
  align-items: center;
  gap: 8px;
}

.form-check-input {
  width: 16px;
  height: 16px;
}

.form-check-label {
  font-size: 14px;
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
  position: relative;
}

.submit-btn:hover {
  background-color: #0056b3;
}

.submit-btn:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.error-message {
  color: #dc3545;
  font-size: 14px;
  margin: 2px 0 0 0;
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

.spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255,255,255,0.3);
  border-radius: 50%;
  border-top-color: #fff;
  animation: spin 1s ease-in-out infinite;
  margin-right: 8px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #555;
}

.close-btn:hover {
  color: black;
}

.alert {
  padding: 12px;
  border-radius: 5px;
  margin-bottom: 15px;
}

.alert-danger {
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  color: #721c24;
}

.alert-success {
  background-color: #d4edda;
  border: 1px solid #c3e6cb;
  color: #155724;
}
</style>