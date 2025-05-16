<template>
  <div class="home-container">
    <div class="hero-section">
      <h1>Hệ thống giám sát an ninh</h1>
      <p class="tagline">Giải pháp theo dõi và cảnh báo phát hiện cháy và xâm nhập trái phép</p>
      <div class="button-group" v-if="!isLoggedIn">
        <router-link to="/login" class="btn btn-primary">Đăng nhập</router-link>
        <router-link to="/register" class="btn btn-secondary">Đăng ký</router-link>
      </div>
      <div v-else>
        <router-link to="/dashboard" class="btn btn-primary">Truy cập Dashboard</router-link>
      </div>
    </div>

    <div class="features-section">
      <h2>Tính năng chính</h2>
      <div class="features-grid">
        <div class="feature-card">
          <div class="feature-icon">🔥</div>
          <h3>Phát hiện cháy</h3>
          <p>Phát hiện nhanh chóng và cảnh báo ngay khi có dấu hiệu cháy</p>
        </div>
        
        <div class="feature-card">
          <div class="feature-icon">🛡️</div>
          <h3>Phát hiện xâm nhập</h3>
          <p>Giám sát và phân tích mạng để phát hiện các cuộc tấn công mạng</p>
        </div>
        
        <div class="feature-card">
          <div class="feature-icon">📊</div>
          <h3>Giám sát thời gian thực</h3>
          <p>Theo dõi các thông số nhiệt độ, độ ẩm và trạng thái hệ thống liên tục</p>
        </div>
        
        <div class="feature-card">
          <div class="feature-icon">⚡</div>
          <h3>Cảnh báo tức thời</h3>
          <p>Nhận thông báo ngay lập tức khi phát hiện các sự cố</p>
        </div>
      </div>
    </div>

    <div class="about-section">
      <h2>Về hệ thống của chúng tôi</h2>
      <p>
        Hệ thống giám sát an ninh của chúng tôi sử dụng công nghệ tiên tiến để phát hiện cháy và 
        các cuộc tấn công mạng, đảm bảo an toàn cho không gian sống và làm việc của bạn. 
        Với giao diện thân thiện và dễ sử dụng, bạn có thể theo dõi mọi thông số quan trọng 
        từ bất kỳ đâu, bất kỳ lúc nào.
      </p>
      <p>
        Được phát triển bởi đội ngũ chuyên gia an ninh và phòng cháy chữa cháy, 
        hệ thống của chúng tôi mang lại sự an tâm và bảo vệ toàn diện cho người dùng.
      </p>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { auth } from '../firebase';
import { onAuthStateChanged } from 'firebase/auth';

export default {
  setup() {
    const isLoggedIn = ref(false);

    onMounted(() => {
      onAuthStateChanged(auth, (user) => {
        isLoggedIn.value = !!user;
      });
    });

    return {
      isLoggedIn
    };
  }
};
</script>

<style scoped>
.home-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.hero-section {
  text-align: center;
  padding: 60px 20px;
  background-color: #f8f9fa;
  border-radius: 10px;
  margin-bottom: 40px;
}

.tagline {
  font-size: 18px;
  color: #6c757d;
  margin-bottom: 30px;
}

.button-group {
  display: flex;
  justify-content: center;
  gap: 20px;
}

.btn {
  display: inline-block;
  padding: 12px 24px;
  border-radius: 5px;
  font-weight: bold;
  text-decoration: none;
  transition: all 0.3s ease;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-primary:hover {
  background-color: #0056b3;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background-color: #545b62;
}

.features-section {
  margin-bottom: 60px;
}

.features-section h2 {
  text-align: center;
  margin-bottom: 40px;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 30px;
}

.feature-card {
  background-color: #fff;
  border-radius: 10px;
  padding: 30px 20px;
  text-align: center;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-10px);
}

.feature-icon {
  font-size: 40px;
  margin-bottom: 20px;
}

.feature-card h3 {
  margin-bottom: 15px;
  color: #333;
}

.about-section {
  background-color: #f8f9fa;
  padding: 40px;
  border-radius: 10px;
  margin-bottom: 40px;
}

.about-section h2 {
  text-align: center;
  margin-bottom: 20px;
}

.about-section p {
  line-height: 1.6;
  margin-bottom: 15px;
}

@media (max-width: 768px) {
  .features-grid {
    grid-template-columns: 1fr;
  }
  
  .button-group {
    flex-direction: column;
    align-items: center;
  }
}
</style>