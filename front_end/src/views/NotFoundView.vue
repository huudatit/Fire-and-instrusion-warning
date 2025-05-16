<template>
  <div class="not-found-container">
    <div class="error-code">404</div>
    <h1>Không tìm thấy trang</h1>
    <p>Trang bạn đang tìm kiếm không tồn tại hoặc đã được di chuyển.</p>
    <div class="action-buttons">
      <router-link to="/" class="btn-primary">Về trang chủ</router-link>
      <button @click="goBack" class="btn-secondary">Quay lại</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NotFoundView',
  methods: {
    goBack() {
      this.$router.go(-1);
    }
  }
}
</script>

<style scoped>
.not-found-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  min-height: 70vh;
  padding: 2rem;
}

.error-code {
  font-size: 8rem;
  font-weight: bold;
  color: #007bff;
  line-height: 1;
  margin-bottom: 1rem;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
}

h1 {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

p {
  font-size: 1.2rem;
  color: #666;
  max-width: 600px;
  margin-bottom: 2rem;
}

.action-buttons {
  display: flex;
  gap: 1rem;
}

.btn-primary {
  background-color: #007bff;
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 5px;
  font-weight: 500;
  transition: background-color 0.3s ease;
}

.btn-primary:hover {
  background-color: #0056b3;
}

.btn-secondary {
  background-color: transparent;
  color: #666;
  border: 1px solid #ccc;
  padding: 0.75rem 1.5rem;
  border-radius: 5px;
  font-weight: 500;
  transition: all 0.3s ease;
  cursor: pointer;
}

.btn-secondary:hover {
  background-color: #f5f5f5;
  border-color: #999;
}

@media (max-width: 576px) {
  .error-code {
    font-size: 6rem;
  }
  
  h1 {
    font-size: 2rem;
  }
  
  .action-buttons {
    flex-direction: column;
  }
}
</style>