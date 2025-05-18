<template>
  <div class="admin-tools">
    <h3>Công cụ quản trị</h3>
    
    <div class="tool-section">
      <h4>Nâng cấp người dùng thành Admin</h4>
      <div class="input-group">
        <input 
          type="text" 
          v-model="userIdToUpgrade" 
          placeholder="Nhập ID của người dùng" 
          class="admin-input"
        />
        <button @click="upgradeUser" class="admin-btn">Nâng cấp</button>
      </div>
      <div v-if="upgradeMessage" :class="['message', upgradeSuccess ? 'success' : 'error']">
        {{ upgradeMessage }}
      </div>
    </div>
    
    <div class="tool-section">
      <h4>Thu hồi quyền Admin</h4>
      <div class="input-group">
        <input 
          type="text" 
          v-model="userIdToRevoke" 
          placeholder="Nhập ID của Admin" 
          class="admin-input"
        />
        <button @click="revokeAdmin" class="admin-btn">Thu hồi quyền</button>
      </div>
      <div v-if="revokeMessage" :class="['message', revokeSuccess ? 'success' : 'error']">
        {{ revokeMessage }}
      </div>
    </div>
    
    <div class="tool-section">
      <h4>Kiểm tra ID của bạn</h4>
      <div v-if="currentUser" class="user-info">
        <p><strong>ID của bạn:</strong> {{ currentUser.uid }}</p>
        <p><strong>Email:</strong> {{ currentUser.email }}</p>
      </div>
      <div v-else class="message error">
        Không có thông tin người dùng
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { auth } from '../firebase';
import { upgradeToAdmin, revokeAdminRights } from '../utils/adminTools';

export default {
  name: 'AdminTools',
  setup() {
    const userIdToUpgrade = ref('');
    const userIdToRevoke = ref('');
    const upgradeMessage = ref('');
    const revokeMessage = ref('');
    const upgradeSuccess = ref(false);
    const revokeSuccess = ref(false);
    const currentUser = ref(null);
    
    onMounted(() => {
      // Lấy thông tin người dùng hiện tại
      currentUser.value = auth.currentUser;
    });
    
    const upgradeUser = async () => {
      if (!userIdToUpgrade.value) {
        upgradeMessage.value = 'Vui lòng nhập ID người dùng';
        upgradeSuccess.value = false;
        return;
      }
      
      try {
        const result = await upgradeToAdmin(userIdToUpgrade.value);
        upgradeMessage.value = result.message;
        upgradeSuccess.value = result.success;
        if (result.success) {
          userIdToUpgrade.value = ''; // Xóa input nếu thành công
        }
      } catch (error) {
        upgradeMessage.value = `Lỗi: ${error.message}`;
        upgradeSuccess.value = false;
      }
    };
    
    const revokeAdmin = async () => {
      if (!userIdToRevoke.value) {
        revokeMessage.value = 'Vui lòng nhập ID admin';
        revokeSuccess.value = false;
        return;
      }
      
      try {
        const result = await revokeAdminRights(userIdToRevoke.value);
        revokeMessage.value = result.message;
        revokeSuccess.value = result.success;
        if (result.success) {
          userIdToRevoke.value = ''; // Xóa input nếu thành công
        }
      } catch (error) {
        revokeMessage.value = `Lỗi: ${error.message}`;
        revokeSuccess.value = false;
      }
    };
    
    return {
      userIdToUpgrade,
      userIdToRevoke,
      upgradeMessage,
      revokeMessage,
      upgradeSuccess,
      revokeSuccess,
      currentUser,
      upgradeUser,
      revokeAdmin
    };
  }
};
</script>

<style scoped>
.admin-tools {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  padding: 20px;
  margin-bottom: 20px;
}

.tool-section {
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.tool-section:last-child {
  border-bottom: none;
  padding-bottom: 0;
  margin-bottom: 0;
}

h3 {
  margin-top: 0;
  color: #333;
  font-size: 1.5rem;
  margin-bottom: 20px;
}

h4 {
  color: #555;
  margin-bottom: 12px;
  font-size: 1.1rem;
}

.input-group {
  display: flex;
  margin-bottom: 10px;
}

.admin-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.admin-btn {
  background-color: #4CAF50;
  color: white;
  border: none;
  padding: 8px 16px;
  margin-left: 10px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
}

.admin-btn:hover {
  background-color: #45a049;
}

.message {
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 14px;
  margin-top: 10px;
}

.success {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.error {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.user-info {
  background-color: #f8f9fa;
  padding: 15px;
  border-radius: 4px;
  font-size: 14px;
}

.user-info p {
  margin: 5px 0;
}
</style>