<template>
  <div class="profile-container">
    <div v-if="loading" class="loading-state">
      <p>Đang tải thông tin...</p>
    </div>
    
    <div v-else-if="!user" class="error-state">
      <p>Bạn cần đăng nhập để xem trang này.</p>
      <router-link to="/login" class="btn btn-primary">Đăng nhập</router-link>
    </div>
    
    <div v-else class="profile-content">
      <div class="profile-header">
        <div class="profile-avatar">
          {{ getUserInitials() }}
        </div>
        <h2>{{ userData.name || 'Người dùng' }}</h2>
        <p class="user-email">{{ user.email }}</p>
        <p class="user-role">Vai trò: {{ userData.role || 'Người dùng' }}</p>
        <p class="join-date">Thành viên từ: {{ formatDate(userData.createdAt) }}</p>
      </div>
      
      <div class="profile-actions">
        <button class="btn btn-secondary" @click="editMode = !editMode">
          {{ editMode ? 'Hủy' : 'Chỉnh sửa thông tin' }}
        </button>
        <button class="btn btn-danger" @click="logout">Đăng xuất</button>
      </div>
      
      <div v-if="editMode" class="edit-profile-form">
        <h3>Chỉnh sửa thông tin</h3>
        <form @submit.prevent="updateProfile">
          <div class="form-group">
            <label for="displayName">Họ và tên:</label>
            <input 
              type="text" 
              id="displayName" 
              v-model="formData.name" 
              required
            />
          </div>
          
          <div class="form-group">
            <label for="phone">Số điện thoại:</label>
            <input 
              type="tel" 
              id="phone" 
              v-model="formData.phone"
            />
          </div>
          
          <div class="form-group">
            <label for="address">Địa chỉ:</label>
            <textarea 
              id="address" 
              v-model="formData.address" 
              rows="3"
            ></textarea>
          </div>
          
          <button type="submit" class="btn btn-primary" :disabled="updateLoading">
            {{ updateLoading ? 'Đang cập nhật...' : 'Lưu thay đổi' }}
          </button>
        </form>
      </div>
      
      <div v-else class="profile-details">
        <h3>Thông tin cá nhân</h3>
        <div class="detail-row">
          <span class="detail-label">Email:</span>
          <span class="detail-value">{{ user.email }}</span>
        </div>
        
        <div class="detail-row">
          <span class="detail-label">Số điện thoại:</span>
          <span class="detail-value">{{ userData.phone || 'Chưa cập nhật' }}</span>
        </div>
        
        <div class="detail-row">
          <span class="detail-label">Địa chỉ:</span>
          <span class="detail-value">{{ userData.address || 'Chưa cập nhật' }}</span>
        </div>
      </div>
      
      <div class="profile-stats">
        <h3>Thống kê hoạt động</h3>
        <div class="stats-cards">
          <div class="stat-card">
            <span class="stat-value">{{ userData.visitCount || 0 }}</span>
            <span class="stat-label">Lượt truy cập</span>
          </div>
          
          <div class="stat-card">
            <span class="stat-value">{{ userData.lastLogin ? formatDate(userData.lastLogin) : 'N/A' }}</span>
            <span class="stat-label">Đăng nhập gần nhất</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { auth, db } from '../firebase';
import { onAuthStateChanged, signOut } from 'firebase/auth';
import { doc, getDoc, updateDoc, serverTimestamp } from 'firebase/firestore';

export default {
  setup() {
    const user = ref(null);
    const userData = ref({});
    const loading = ref(true);
    const editMode = ref(false);
    const updateLoading = ref(false);
    const router = useRouter();
    
    const formData = reactive({
      name: '',
      phone: '',
      address: ''
    });
    
    const loadUserData = async (userId) => {
      try {
        const userDoc = await getDoc(doc(db, "users", userId));
        if (userDoc.exists()) {
          userData.value = userDoc.data();
          
          // Cập nhật formData
          formData.name = userData.value.name || '';
          formData.phone = userData.value.phone || '';
          formData.address = userData.value.address || '';
          
          // Cập nhật lượt truy cập
          updateDoc(doc(db, "users", userId), {
            visitCount: (userData.value.visitCount || 0) + 1,
            lastLogin: serverTimestamp()
          });
        }
      } catch (error) {
        console.error("Lỗi khi tải dữ liệu người dùng:", error);
      } finally {
        loading.value = false;
      }
    };
    
    onMounted(() => {
      onAuthStateChanged(auth, (currentUser) => {
        if (currentUser) {
          user.value = currentUser;
          loadUserData(currentUser.uid);
        } else {
          user.value = null;
          loading.value = false;
        }
      });
    });
    
    const getUserInitials = () => {
      if (!userData.value.name) return '?';
      return userData.value.name
        .split(' ')
        .map(name => name.charAt(0))
        .join('')
        .toUpperCase()
        .slice(0, 2);
    };
    
    const formatDate = (timestamp) => {
      if (!timestamp) return 'N/A';
      
      if (timestamp.toDate) {
        // Firestore timestamp
        const date = timestamp.toDate();
        return new Intl.DateTimeFormat('vi-VN', { 
          day: '2-digit', 
          month: '2-digit', 
          year: 'numeric' 
        }).format(date);
      } else {
        // Javascript Date
        return new Intl.DateTimeFormat('vi-VN', { 
          day: '2-digit', 
          month: '2-digit', 
          year: 'numeric' 
        }).format(new Date(timestamp));
      }
    };
    
    const updateProfile = async () => {
      if (!user.value) return;
      
      updateLoading.value = true;
      
      try {
        await updateDoc(doc(db, "users", user.value.uid), {
          name: formData.name,
          phone: formData.phone,
          address: formData.address,
          updatedAt: serverTimestamp()
        });
        
        // Cập nhật userData hiển thị
        userData.value = {
          ...userData.value,
          name: formData.name,
          phone: formData.phone,
          address: formData.address
        };
        
        // Tắt chế độ chỉnh sửa
        editMode.value = false;
      } catch (error) {
        console.error("Lỗi khi cập nhật hồ sơ:", error);
        alert("Không thể cập nhật hồ sơ. Vui lòng thử lại.");
      } finally {
        updateLoading.value = false;
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
    
    return {
      user,
      userData,
      loading,
      editMode,
      formData,
      updateLoading,
      getUserInitials,
      formatDate,
      updateProfile,
      logout
    };
  }
};
</script>

<style scoped>
.profile-container {
  max-width: 800px;
  margin: 40px auto;
  padding: 20px;
}

.loading-state,
.error-state {
  text-align: center;
  padding: 40px;
}

.profile-content {
  background-color: #fff;
  border-radius: 10px;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.profile-header {
  background-color: #007bff;
  color: white;
  text-align: center;
  padding: 30px 20px;
  position: relative;
}

.profile-avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background-color: white;
  color: #007bff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36px;
  font-weight: bold;
  margin: 0 auto 20px;
}

.user-email {
  opacity: 0.8;
  margin-top: 5px;
}

.user-role {
  display: inline-block;
  background-color: rgba(255, 255, 255, 0.2);
  padding: 5px 15px;
  border-radius: 20px;
  margin-top: 15px;
}

.join-date {
  font-size: 14px;
  margin-top: 10px;
  opacity: 0.8;
}

.profile-actions {
  display: flex;
  justify-content: center;
  padding: 20px;
  gap: 15px;
  border-bottom: 1px solid #eee;
}

.btn {
  padding: 10px 20px;
  border-radius: 5px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: background-color 0.3s ease;
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
  background-color: #5a6268;
}

.btn-danger {
  background-color: #dc3545;
  color: white;
}

.btn-danger:hover {
  background-color: #c82333;
}

.edit-profile-form,
.profile-details {
  padding: 30px;
  border-bottom: 1px solid #eee;
}

.edit-profile-form h3,
.profile-details h3,
.profile-stats h3 {
  margin-top: 0;
  margin-bottom: 20px;
  font-weight: 500;
  color: #333;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #555;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 16px;
}

.detail-row {
  display: flex;
  margin-bottom: 15px;
  border-bottom: 1px solid #f0f0f0;
  padding-bottom: 15px;
}

.detail-label {
  font-weight: 500;
  width: 130px;
  color: #555;
}

.detail-value {
  flex: 1;
  color: #333;
}

.profile-stats {
  padding: 30px;
}

.stats-cards {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  justify-content: space-around;
}

.stat-card {
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  width: 200px;
  text-align: center;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
}

.stat-value {
  display: block;
  font-size: 24px;
  font-weight: bold;
  color: #007bff;
  margin-bottom: 10px;
}

.stat-label {
  display: block;
  color: #6c757d;
  font-size: 14px;
}

@media (max-width: 768px) {
  .profile-actions {
    flex-direction: column;
  }
  
  .detail-row {
    flex-direction: column;
  }
  
  .detail-label {
    width: 100%;
    margin-bottom: 5px;
  }
  
  .stats-cards {
    flex-direction: column;
    align-items: center;
  }
  
  .stat-card {
    width: 100%;
  }
}
</style>